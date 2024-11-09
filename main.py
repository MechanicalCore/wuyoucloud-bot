import json
import asyncio
import os
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, ContextTypes
from datetime import datetime
from config import load_config
from scraper import scrape_all_websites, update_inventory_json
from message_formatter import (
    format_inventory_message,
    format_task_submitted,
    format_task_in_queue,
    format_inventory_blocked_notification,
    format_release_notification,
    format_sold_out_notification,
    format_error_notification,
    format_admin_error_notification
)
from apscheduler.schedulers.background import BackgroundScheduler
from queue import Queue
from threading import Timer

# 加载配置
config = load_config()
BOT_TOKEN = config["telegram_bot_token"]
GROUP_IDS = config["notification_group_ids"]
ADMIN_IDS = config["admin_user_ids"]
INVENTORY_FILE = "inventory.json"

# 定义任务队列
task_queue = Queue(maxsize=1)  # 限制同时只能有一个任务

# 定时任务调度器
scheduler = BackgroundScheduler()
scheduler.start()

# 定义按钮
def create_goto_website_button():
    return InlineKeyboardMarkup([[InlineKeyboardButton("前往官网", url="web url")]])

# 处理 /start 命令
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! This is a test bot", reply_markup=create_goto_website_button())

# 检查请求是否来自群组
def is_from_group(update: Update):
    return update.effective_chat.type in ["group", "supergroup"]

# 读取 JSON 文件库存信息并发送
async def send_inventory(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_id = update.message.from_user.id

    # 检查任务队列状态
    if task_queue.full():
        await update.message.reply_text(format_task_in_queue(), reply_markup=create_goto_website_button())
        return

    # 提交任务并通知用户
    task_queue.put("send_inventory")
    await update.message.reply_text(format_task_submitted(), reply_markup=create_goto_website_button())

    try:
        # 从 JSON 文件中读取库存信息
        if not os.path.exists(INVENTORY_FILE):
            await update.message.reply_text("库存数据暂时不可用。请稍后再试。")
            task_queue.get()
            return

        with open(INVENTORY_FILE, "r") as f:
            inventory_data = json.load(f)

        # 格式化库存信息，并过滤无库存商品
        inventory_data = [item for item in inventory_data if item["stock"] > 0]
        message_text = format_inventory_message(inventory_data)
        sent_message = await context.bot.send_message(chat_id=chat_id, text=message_text, parse_mode="MarkdownV2", reply_markup=create_goto_website_button())

        # 设置定时器，1 分钟后删除消息
        Timer(60, lambda: sent_message.delete()).start()
    except Exception as e:
        await update.message.reply_text(format_error_notification(), reply_markup=create_goto_website_button())
        for admin_id in ADMIN_IDS:
            await context.bot.send_message(admin_id, format_admin_error_notification("库存查询", str(e)), parse_mode="MarkdownV2")
    finally:
        task_queue.get()  # 任务完成，移出队列

# 每分钟检查库存变动
async def check_inventory_changes(context: ContextTypes.DEFAULT_TYPE):
    await update_inventory_json()  # 更新 JSON 文件
    with open(INVENTORY_FILE, "r") as f:
        current_inventory = json.load(f)

    if task_queue.full():
        return

    # 比较库存信息
    new_releases = [item for item in current_inventory if item["stock"] > 0 and item.get("previous_stock", 0) == 0]
    sold_out_items = [item for item in current_inventory if item["stock"] == 0 and item.get("previous_stock", 1) > 0]

    if new_releases or sold_out_items:
        task_queue.put("inventory_check")
        try:
            # 发送新增库存通知
            if new_releases:
                release_message = format_release_notification(new_releases)
                for group_id in GROUP_IDS:
                    await context.bot.send_message(chat_id=group_id, text=release_message, parse_mode="MarkdownV2", reply_markup=create_goto_website_button())

            # 发送售罄通知
            if sold_out_items:
                sold_out_message = format_sold_out_notification(sold_out_items)
                for group_id in GROUP_IDS:
                    await context.bot.send_message(chat_id=group_id, text=sold_out_message, parse_mode="MarkdownV2", reply_markup=create_goto_website_button())

            # 更新每个商品的 previous_stock
            for item in current_inventory:
                item["previous_stock"] = item["stock"]
            with open(INVENTORY_FILE, "w") as f:
                json.dump(current_inventory, f)
        finally:
            task_queue.get()

# 主函数
async def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("kc", send_inventory))

    # 初始化时爬取库存信息并写入 JSON 文件
    print("初始化爬取库存信息...")
    await update_inventory_json()
    print("库存信息已更新至 JSON 文件")

    # 每分钟执行库存更新检查
    scheduler.add_job(lambda: asyncio.create_task(check_inventory_changes(app.bot)), "interval", minutes=1)

    print("Bot 已启动")
    await app.start()
    await app.updater.start_polling()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
