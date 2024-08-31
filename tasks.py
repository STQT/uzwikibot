import asyncio

import logging
from datetime import timedelta, datetime

from utils import WikiApi

api = WikiApi()
interval_seconds = 10
interval_seconds_edits = 5
database_list_limit = 20
database_list_limit_edit = 20
channel_link = "@uzwikinewpages"
channel_link_edit = "@uzwikinewedits"


async def clean_up_database(collwikis):
    """
    Cleans up the collwikis collection if it exceeds 250 documents by deleting the oldest entries
    based on the timestamp field.
    """
    # Count total documents in the collection
    total_documents = await collwikis.count_documents({})

    # Define the document limit
    document_limit = 250
    if total_documents > document_limit:
        # Calculate how many documents need to be deleted
        documents_to_delete = total_documents - document_limit - 50
        # Find the oldest documents based on the timestamp
        oldest_documents = collwikis.find({}).sort('timestamp', 1).limit(documents_to_delete)
        # Extract the _id of the documents to be deleted
        oldest_ids = [doc['_id'] for doc in await oldest_documents.to_list(length=documents_to_delete)]
        # Delete the documents with the collected _id values
        await collwikis.delete_many({'_id': {'$in': oldest_ids}})
        # Log the deletion
        logging.info(f"Deleted {documents_to_delete} old documents from collwikis.")


async def get_last_created_page(bot, collwikis, colledits):
    data = api.get_new_pages()
    # fountain_link = "https://fountain.toolforge.org/editathons/wiki-stipendiya-marafoni"
    fountain_link = "https://fountain.toolforge.org/editathons/wikistipendiyafinal"
    recent_list: list = data['query']['recentchanges']
    for i in recent_list:
        i.update({
            "_id": i.get('pageid'),
        })

    recent_db_list = collwikis.find({}).sort('_id', -1)
    recent_db_ids = [a.get('_id') for a in await recent_db_list.to_list(length=database_list_limit)]

    new_page_obj = []

    for x in recent_list:
        if x.get('pageid') not in recent_db_ids:
            new_page_obj.append(x)
    if new_page_obj:
        await collwikis.insert_many(
            [i for i in new_page_obj])
        for page in new_page_obj:
            vaqt = datetime.strptime(page['timestamp'], "%Y-%m-%dT%H:%M:%SZ") + timedelta(hours=5)
            await bot.send_message(channel_link, "<b>Yangi sahifa!</b>\n"
                                                 "Nomi: <a href=\"https://uz.wikipedia.org/wiki/{title}\">"
                                                 "{title}</a>\n"
                                                 "Foydalanuvchi: {user}\n"
                                                 "Hajmi: {newlen}\n"
                                                 "Vaqti: {vaqt}".format(title=page['title'],
                                                                        user=page['user'],
                                                                        newlen=page['newlen'],
                                                                        vaqt=vaqt.strftime("%H:%M:%S")),
                                   parse_mode="HTML", disable_web_page_preview=True)
            await asyncio.sleep(0.05)
        await clean_up_database(collwikis)
    else:
        logging.info("NO CHANGES")

    return True


async def get_last_edited_pages(bot, collwikis, colledits):
    data = api.get_last_edits()
    recent_list = data['query']['recentchanges']
    for edit in recent_list:
        edit['_id'] = edit['rcid']

    recent_db_list = colledits.find({}).sort('_id', -1)
    recent_db_ids = [a.get('_id') for a in await recent_db_list.to_list(length=database_list_limit_edit)]

    new_edits = []

    for edit in recent_list:
        if edit['_id'] not in recent_db_ids:
            new_edits.append(edit)

    if new_edits:
        await colledits.insert_many(new_edits)
        for edit in new_edits:
            size = edit['newlen'] - edit['oldlen']
            size = f"+{size}" if size > 0 else str(size)
            formatted_time = datetime.strptime(edit['timestamp'], "%Y-%m-%dT%H:%M:%SZ") + timedelta(hours=5)
            diff_url = (
                f"https://uz.wikipedia.org/w/index.php?title={edit['title'].replace(' ', '_')}"
                f"&curid={edit['pageid']}&diff={edit['revid']}&oldid={edit['old_revid']}"
            )
            text = (
                f"<b>Maqola:</b> <a href=\"https://uz.wikipedia.org/wiki/{edit['title']}\">{edit['title']}</a>\n"
                f"<b>O‘zgargan hajm:</b> {size}\n"
                f"<b>Foydalanuvchi:</b> {edit['user']}\n"
                f"<b>Vaqti:</b> {formatted_time.strftime('%H:%M:%S')}\n"
                f"<b>O‘zgarishlarni ko‘rish:</b> <a href=\"{diff_url}\">Farqini ko‘rish</a>"
            )
            # Send the message to the Telegram channel
            await bot.send_message(channel_link_edit, text, parse_mode="HTML", disable_web_page_preview=True)
        await clean_up_database(colledits)
    else:
        logging.info("NO NEW EDITS")
    return True


def set_scheduled_jobs(scheduler, *args, **kwargs):
    # Adding tasks to scheduler
    scheduler.add_job(get_last_created_page, "interval", seconds=interval_seconds, args=args)
    scheduler.add_job(get_last_edited_pages, "interval", seconds=interval_seconds_edits, args=args)
    # scheduler.add_job(clear_notifications_per_day, "interval", seconds=10)
