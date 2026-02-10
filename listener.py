import redis

from db import read_remind

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

r.config_set('notify-keyspace-events', 'Ex')

print("=== Слушатель напоминаний запущен ===")
print("Ожидаю события...\n")

pubsub = r.pubsub()

pubsub.psubscribe('__keyevent@0__:expired')

for message in pubsub.listen():
    if message['type'] == 'pmessage':
        expired_key = message['data']

        print(f"⏰ Событие получено!")
        print(f"   Тип: {message['type']}")
        print(f"   Канал: {message['channel']}")
        print(f"   Истёкший ключ: {expired_key}")

        if expired_key.startswith('reminder:'):
            reminder_id = expired_key.split(':')[1]
            text = read_remind(reminder_id)
            print(f"\n🔔 НАПОМИНАНИЕ (ID: {reminder_id})")
            print(f"Напоминание: {text}")
            print()