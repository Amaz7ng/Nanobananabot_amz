import logging
from sqlalchemy import update
from sqlalchemy.exc import SQLAlchemyError

from bot.database.models import User
from bot.database.db_setup import async_session

logger = logging.getLogger(__name__)

async def add_generations_to_user_balance(user_id: int, attempts_count: int) -> bool:

    logger.info(f"⏳ Попытка начисления {attempts_count} попыток пользователю {user_id}...")

    async with async_session() as session:
        try:
            stmt = (
                update(User)
                .where(User.telegram_id == user_id)
                .values(balance=User.balance + attempts_count)
            )

            result = await session.execute(stmt)
            await session.commit()

            if result.rowcount == 0:
                logger.warning(f"⚠️ Пользователь с telegram_id {user_id} не найден в БД. Начисление не произошло.")
                return False

            logger.info(f"✅ Успешно зачислено {attempts_count} попыток пользователю {user_id}.")
            return True

        except SQLAlchemyError as e:
            await session.rollback()
            logger.error(f"❌ Ошибка SQLAlchemy при начислении попыток пользователю {user_id}: {e}")
            return False
        except Exception as e:
            await session.rollback()
            logger.error(f"❌ Непредвиденная ошибка при начислении попыток пользователю {user_id}: {e}")
            return False