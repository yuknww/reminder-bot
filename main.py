import redis
import time
from db import create_remind
r = redis.Redis(host='localhost', port=6379, decode_responses=True)

print("=== Добавление напоминания ===")

text = input("Что напомнить? ")
seconds = int(input("Через сколько секунд? "))

reminder_id = int(time.time())

key = f'reminder:{reminder_id}'
r.setex(key, seconds, text)

print(f"\n✓ Напоминание создано!")
print(f"  ID: {reminder_id}")
print(f"  Текст: {text}")
print(f"  Сработает через {seconds} секунд")
print(f"  Ключ в Redis: {key}")
create_remind(reminder_id, text, seconds)

ttl = r.ttl(key)
print(f"\n  Осталось времени: {ttl} секунд")