#!/bin/bash

# ========== 配置区 ==========
APP_HOME="/opt/ManageSystem/server"
VENV_BIN="$APP_HOME/venv/bin"
UWSGI_BIN="$VENV_BIN/uwsgi"
UWSGI_INI="$APP_HOME/uwsgi.ini"
PID_FILE="$APP_HOME/uwsgi.pid"
# ===========================

# 加载全局环境变量（谨慎使用，可能引入副作用）
# source /etc/profile

# 检查必要文件是否存在
if [ ! -d "$APP_HOME" ]; then
    echo "ERROR: APP_HOME does not exist: $APP_HOME" >&2
    exit 1
fi

if [ ! -x "$UWSGI_BIN" ]; then
    echo "ERROR: uWSGI executable not found or not executable: $UWSGI_BIN" >&2
    exit 1
fi

if [ ! -f "$UWSGI_INI" ]; then
    echo "ERROR: uWSGI config file not found: $UWSGI_INI" >&2
    exit 1
fi

# 检查 uwsgi 是否已在运行（统一函数）
is_running() {
    if [ -f "$PID_FILE" ]; then
        local pid
        pid=$(cat "$PID_FILE" 2>/dev/null)
        if [ -n "$pid" ] && [ "$pid" -gt 0 ] 2>/dev/null && kill -0 "$pid" 2>/dev/null; then
            return 0  # 正在运行
        else
            rm -f "$PID_FILE" 2>/dev/null  # 清理无效 PID 文件
        fi
    fi
    return 1  # 未运行
}

start() {
    echo "Starting uWSGI server..."

    if is_running; then
        echo "uWSGI is already running (PID: $(cat "$PID_FILE"))" >&2
        exit 1
    fi

    cd "$APP_HOME" || { echo "ERROR: Failed to cd to $APP_HOME" >&2; exit 1; }

    # 启动 uWSGI（前台启动，由 systemd 或 supervisord 管理时更合适）
    # 如果你希望后台运行，确保 uwsgi.ini 中有 master = true 和 pidfile 配置
    "$UWSGI_BIN" --ini "$UWSGI_INI"

    # 等待 PID 文件生成（最多 5 秒）
    local count=0
    while [ ! -f "$PID_FILE" ] && [ $count -lt 5 ]; do
        sleep 1
        ((count++))
    done

    if is_running; then
        echo "uWSGI started successfully (PID: $(cat "$PID_FILE"))"
    else
        echo "ERROR: uWSGI failed to start (PID file not created)" >&2
        exit 1
    fi
}

stop() {
    echo "Stopping uWSGI server..."

    if ! is_running; then
        echo "uWSGI is NOT running." >&2
        return 1
    fi

    local pid
    pid=$(cat "$PID_FILE")

    echo "Gracefully stopping uWSGI (PID: $pid)..."
    "$UWSGI_BIN" --stop "$PID_FILE" >/dev/null 2>&1

    # 等待最多 15 秒（兼容非 Bash shell）
    local i=0
    while [ $i -lt 15 ]; do
        if ! kill -0 "$pid" 2>/dev/null; then
            echo "uWSGI stopped gracefully."
            rm -f "$PID_FILE"
            return 0
        fi
        sleep 1
        ((i++))
    done

    # 超时后强制 kill
    echo "Graceful stop timed out. Force killing PID $pid..."
    kill -9 "$pid" 2>/dev/null
    rm -f "$PID_FILE"
}

restart() {
    stop
    sleep 2
    start
}

status() {
    if is_running; then
        echo "uWSGI is running (PID: $(cat "$PID_FILE"))."
        return 0
    else
        echo "uWSGI is NOT running."
        return 1
    fi
}

# 主逻辑
case "${1:-}" in
    start)
        start
        ;;
    stop)
        stop
        ;;
    restart)
        restart
        ;;
    status)
        status
        ;;
    "")
        echo "Usage: $0 {start|stop|restart|status}" >&2
        exit 1
        ;;
    *)
        echo "Invalid command: $1" >&2
        echo "Usage: $0 {start|stop|restart|status}" >&2
        exit 1
        ;;
esac

exit 0