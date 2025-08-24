from app.bots.post_generation_bots import (
    run_pregame_bot, run_postgame_focus_bot, run_realtime_bot, run_trend_bot
)

def manual_run(bot_type: str, topic: str = None):
    print(f"🔧 수동 실행 - bot_type: {bot_type}, topic: {topic}")

    if bot_type == "pregame":
        run_pregame_bot(topic)
    elif bot_type == "realtime":
        run_realtime_bot(topic)
    elif bot_type == "postgame":
        run_postgame_focus_bot(topic)
    elif bot_type == "trend":
        run_trend_bot()
    else:
        print("❌ 지원되지 않는 bot_type")

if __name__ == "__main__":
    bot_type = "postgame"    # pregame / realtime / postgame / trend
    topic = "첼시 리버풀 하이라이트"

    manual_run(bot_type, topic)