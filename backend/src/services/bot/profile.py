from schemas.config_schemas import ModuleConfig
from core.customer import Customer
import qrcode
from io import BytesIO
from loguru import logger


class ProfileService:
    @classmethod
    async def get_qr(cls, config: ModuleConfig, customer: Customer) -> BytesIO:
        try:
            qr_data = {}

            if config.qr_data.first_name:
                qr_data["first_name"] = customer.first_name
            if config.qr_data.last_name:
                qr_data["last_name"] = customer.last_name
            if config.qr_data.phone:
                qr_data["phone"] = customer.phone
            if config.qr_data.chat_id:
                qr_data["chat_id"] = customer.chat_id

            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(str(qr_data))
            qr.make(fit=True)

            # Создаем изображение QR-кода
            img = qr.make_image(fill_color="black", back_color="white")

            # Конвертируем в bytes для отправки через Telegram
            buf = BytesIO()
            img.save(buf, format="PNG")
            buf.seek(0)
            return buf
        except Exception as e:
            logger.error(f"Error generating QR code: {e}")
            return "Не удалось сгенерировать QR-код"
