#!/bin/bash

# ========== 配置区 ==========
APP_HOME="/opt/ManageSystem/server"
VENV_BIN="$APP_HOME/venv/bin"
UWSGI_BIN="$VENV_BIN/uwsgi"
UWSGI_INI="$APP_HOME/uwsgi.ini"
PID_FILE="$APP_HOME/uwsgi.pid"
# ===========================

# 加载全局环境变量
source /etc/profile

start() {
    echo "Starting uWSGI server..."
    if [ -f "$PID_FILE" ]; then
        echo "PID file exists: $PID_FILE. Checking if process is running..."
        if kill -0 $(cat "$PID_FILE") 2>/dev/null; then
            echo "uWSGI is already running (PID: $(cat "$PID_FILE"))"
            exit 1
        else
            echo "Stale PID file found. Removing it."
            rm -f "$PID_FILE"
        fi
    fi

    cd "$APP_HOME" || { echo "Failed to cd to $APP_HOME"; exit 1; }
    "$UWSGI_BIN" --ini "$UWSGI_INI"

    # 等待启动完成（简单检查）
    sleep 2
    if [ -f "$PID_FILE" ]; then
        echo "uWSGI started successfully (PID: $(cat "$PID_FILE"))"
    else
        echo "uWSGI may have failed to start (no PID file)"
    fi
}

stop() {
    echo "Stopping uWSGI server..."
    if [ ! -f "$PID_FILE" ]; then
        echo "PID file not found: $PID_FILE. Is uWSGI running?"
        return 1
    fi

    PID=$(cat "$PID_FILE")
    if kill -0 "$PID" 2>/dev/null; then
        echo "Gracefully stopping uWSGI (PID: $PID)..."
        # 使用 uwsgi --stop 实现优雅退出（触发 reload-mercy）
        "$UWSGI_BIN" --stop "$PID_FILE"

        # 等待最多 15 秒
        for i in {1..15}; do
            if ! kill -0 "$PID" 2>/dev/null; then
                echo "uWSGI stopped gracefully."
                rm -f "$PID_FILE"
                return 0
            fi
            sleep 1
        done

        # 超时后强制 kill
        echo "Graceful stop timed out. Force killing PID $PID..."
        kill -9 "$PID" 2>/dev/null
        rm -f "$PID_FILE"
    else
        echo "Process not running. Removing stale PID file."
        rm -f "$PID_FILE"
    fi
}

restart() {
    stop
    sleep 2
    start
}

case "$1" in
    start)
        start
        ;;
    stop)
        stop
        ;;
    restart)
        restart
        ;;
    *)
        echo "Usage: $0 {start|stop|restart}"
        exit 1
        ;;
esac

exit 0
