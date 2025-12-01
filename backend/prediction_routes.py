# backend/prediction_routes.py
from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
import traceback
import sys

from .auth_routes import auth_required
from .services import weather_service, feature_service, model_service, advice_service
from .persistence import prediction_repository

prediction_bp = Blueprint("prediction_bp", __name__, url_prefix="/api")


@prediction_bp.route("/predict", methods=["POST"])
@auth_required
def predict():
    try:
        data = request.get_json() or {}
        required = ["crop", "market", "date"]
        if not all(k in data for k in required):
            return jsonify({"error": "Missing crop/market/date"}), 400

        crop = data["crop"]
        market = data["market"]
        date_str = data["date"]
        lat = data.get("lat")
        lon = data.get("lon")

        if lat is None or lon is None:
            return jsonify({"error": "Latitude and longitude required"}), 400

        lat = float(lat)
        lon = float(lon)

        # ------------ 1) Weather from OpenWeather ------------
        try:
            current_weather, forecast_weather = weather_service.get_weather_and_forecast(
                lat, lon
            )
        except Exception as e:
            traceback.print_exc()
            err = {
                "type": type(e).__name__,
                "str": str(e),
                "args": e.args,
            }
            print("ERROR in weather_service:", err, file=sys.stderr)
            return jsonify({"error": "Weather service failed", "details": err}), 502

        # ------------ 2) Build feature vector ------------
        try:
            feat = feature_service.build_feature_vector(
                crop=crop,
                market=market,
                date_str=date_str,
                lat=lat,
                lon=lon,
                weather_current=current_weather,
            )
        except Exception as e:
            traceback.print_exc()
            err = {
                "type": type(e).__name__,
                "str": str(e),
                "args": e.args,
            }
            print("ERROR in feature_service.build_feature_vector:", err, file=sys.stderr)
            return jsonify(
                {"error": "Feature engineering failed", "details": err}
            ), 500

        # DEBUG: log feature vector
        print("DEBUG feat keys:", list(feat.keys()))
        print("DEBUG feat:", feat)

        # ------------ 3) Predict price for chosen date ------------
        try:
            predicted_price = model_service.predict_price(feat)
        except Exception as e:
            traceback.print_exc()
            err = {
                "type": type(e).__name__,
                "str": str(e),
                "args": e.args,
            }
            print("ERROR in model_service.predict_price (base):", err, file=sys.stderr)
            return jsonify(
                {"error": "Model prediction failed", "details": err}
            ), 500

        print(
            "DEBUG predicted_price (base):",
            predicted_price,
            "type:",
            type(predicted_price),
        )

        base_dt = datetime.fromisoformat(date_str)

        # ------------ 4) Trend: next 3 days predictions ------------
        future_prices = []
        future_series = []
        try:
            for i in range(1, 4):
                dt_future = base_dt + timedelta(days=i)
                feat_future = dict(feat)
                feat_future["DateNumeric"] = model_service.date_to_numeric(dt_future)
                fp = model_service.predict_price(feat_future)
                future_prices.append(fp)
                future_series.append(
                    {
                        "date": dt_future.date().isoformat(),
                        "price": float(fp),
                    }
                )
        except Exception as e:
            traceback.print_exc()
            err = {
                "type": type(e).__name__,
                "str": str(e),
                "args": e.args,
            }
            print(
                "ERROR while predicting future_prices (ignored for now):",
                err,
                file=sys.stderr,
            )
            # we ignore failure for future days; base prediction already done

        # ------------ 5) Confidence band & trend info ------------
        conf_low, conf_high = advice_service.compute_confidence_range(predicted_price)
        trend_dir = advice_service.get_trend_direction(predicted_price, future_prices)
        best_day_info = (
            advice_service.get_best_day_info(base_dt, future_prices)
            if future_prices
            else None
        )

        # ------------ 6) Agro insights ------------
        soil_moisture = feat.get("SoilMoisture(%)", 0.0)
        agro_insights = advice_service.generate_agro_insights(
            crop=crop,
            current_weather=current_weather,
            soil_moisture=soil_moisture,
            forecast_weather=forecast_weather,
        )

        # ------------ 7) Feature-importance story ------------
        feature_summary = advice_service.explain_features(feat, current_weather)

        # ------------ 8) Alternative nearby markets ------------
        alt_markets = feature_service.get_nearby_markets(market)
        alternative_predictions = []
        try:
            for alt in alt_markets:
                alt_feat = dict(feat)
                alt_feat["Market"] = alt
                alt_feat["AgroZone"] = feature_service.determine_agrozone(alt)
                alt_price = model_service.predict_price(alt_feat)
                alternative_predictions.append(
                    {
                        "market": alt,
                        "price": float(alt_price),
                    }
                )
        except Exception as e:
            traceback.print_exc()
            err = {
                "type": type(e).__name__,
                "str": str(e),
                "args": e.args,
            }
            print(
                "ERROR while predicting alternative markets (ignored for now):",
                err,
                file=sys.stderr,
            )
            alternative_predictions = []

        # ------------ 9) Economic advice text ------------
        advice = advice_service.generate_advice(predicted_price, future_prices)

        request_payload = {
            "crop": crop,
            "market": market,
            "date": date_str,
            "lat": lat,
            "lon": lon,
        }

        prediction_id = prediction_repository.save_prediction(
            user_id=request.user_id,
            request_data=request_payload,
            features_used=feat,
            predicted_price=predicted_price,
            advice=advice,
        )

        return jsonify(
            {
                "predictionId": prediction_id,
                "predictedPrice": float(predicted_price),
                "confidenceLower": conf_low,
                "confidenceUpper": conf_high,
                "trendDirection": trend_dir,
                "bestDay": best_day_info,
                "futureSeries": future_series,
                "advice": advice,
                "weather": current_weather,
                "forecastWeather": forecast_weather,
                "agroInsights": agro_insights,
                "featureImportanceSummary": feature_summary,
                "alternativeMarkets": alternative_predictions,
            }
        )

    except Exception as e:
        # Fallback catch-all for anything missed above
        traceback.print_exc()
        err = {
            "type": type(e).__name__,
            "str": str(e),
            "args": e.args,
        }
        print("FATAL ERROR in /api/predict:", err, file=sys.stderr)
        return jsonify(
            {"error": "Model prediction failed (fatal)", "details": err}
        ), 500


@prediction_bp.route("/predict/history", methods=["GET"])
@auth_required
def history():
    preds = prediction_repository.find_by_user(request.user_id)
    out = []
    for p in preds:
        out.append(
            {
                "id": str(p["_id"]),
                "crop": p["request"]["crop"],
                "market": p["request"]["market"],
                "date": p["request"]["date"],
                "predictedPrice": p["predictedPrice"],
                "advice": p.get("advice"),
                "createdAt": p["createdAt"].isoformat(),
                "actualPrice": p.get("actualPrice"),
                "priceDiff": p.get("priceDiff"),
            }
        )
    return jsonify(out)


@prediction_bp.route("/predict/actual", methods=["POST"])
@auth_required
def set_actual_price():
    data = request.get_json() or {}
    if "predictionId" not in data or "actualPrice" not in data:
        return jsonify({"error": "predictionId and actualPrice required"}), 400
    updated = prediction_repository.update_actual_price(
        prediction_id=data["predictionId"],
        actual_price=float(data["actualPrice"]),
    )
    if not updated:
        return jsonify({"error": "Prediction not found"}), 404

    return jsonify(
        {
            "id": str(updated["_id"]),
            "actualPrice": updated["actualPrice"],
            "priceDiff": updated["priceDiff"],
        }
    )


@prediction_bp.route("/heatmap/latest", methods=["GET"])
@auth_required
def heatmap_latest():
    crop = request.args.get("crop")
    rows = prediction_repository.aggregate_by_district(crop=crop, days=7)
    return jsonify(rows)


@prediction_bp.route("/predict/<prediction_id>", methods=["DELETE"])
@auth_required
def delete_prediction(prediction_id):
    ok = prediction_repository.delete_prediction(request.user_id, prediction_id)
    if not ok:
        return jsonify({"error": "Prediction not found"}), 404
    return jsonify({"status": "deleted"})
