from app.bots.post_generation_bots import (
    run_pregame_bot, run_postgame_focus_bot, run_realtime_bot, run_trend_bot
)

def lambda_handler(event, context):
    topic = event.get("topic")
    bot_type = event.get("bot_type")

    if not topic or not bot_type:
        return {"statusCode": 400, "body": "Missing topic or bot_type"}

    if bot_type == "pregame":
        run_pregame_bot(topic)
    elif bot_type == "realtime":
        run_realtime_bot(topic)
    elif bot_type == "postgame":
        run_postgame_focus_bot(topic)
    elif bot_type == "trend":
        run_trend_bot()
    else:
        return {"statusCode": 400, "body": "Invalid bot_type"}

    return {"statusCode": 200, "body": "Bot executed"}