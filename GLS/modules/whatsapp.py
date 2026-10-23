"""
GLORENZA SALON AHMEDABAD - WhatsApp Messaging Engine
Generates URL-encoded direct WhatsApp message links for receipts and booking confirmations.
"""

import urllib.parse


def format_phone_for_whatsapp(phone: str) -> str:
    """Sanitizes Indian mobile numbers into international WhatsApp format (91XXXXXXXXXX)."""
    digits = "".join(filter(str.isdigit, str(phone)))
    if len(digits) == 10:
        return f"91{digits}"
    elif len(digits) == 12 and digits.startswith("91"):
        return digits
    return digits


def generate_invoice_whatsapp_link(receipt_data: dict) -> str:
    """Builds a WhatsApp URL with itemized salon bill summary."""
    phone = format_phone_for_whatsapp(receipt_data.get("client_phone", ""))
    
    items_text = ""
    for idx, it in enumerate(receipt_data.get("items", []), 1):
        stf = f" (By: {it.get('staff_name')})" if it.get("staff_name") else ""
        items_text += f"{idx}. {it['name']} x{it['qty']} - Rs.{it['price'] * it['qty']:,.2f}{stf}\n"

    msg = (
        f" *GLORENZA SALON - AHMEDABAD*\n"
        f"------------------------------------\n"
        f"Dear *{receipt_data.get('client_name')}*,\n"
        f"Thank you for visiting GLORENZA Salon!\n\n"
        f" *Invoice No:* {receipt_data.get('invoice_no')}\n"
        f" *Date:* {receipt_data.get('date')}\n"
        f" *Payment Mode:* {receipt_data.get('pay_method')} (PAID)\n\n"
        f"*Billed Services & Retail:*\n"
        f"{items_text}\n"
        f"Subtotal: Rs.{receipt_data.get('subtotal', 0):,.2f}\n"
        f"Discount: -Rs.{receipt_data.get('discount', 0):,.2f}\n"
        f"GST & Taxes: +Rs.{receipt_data.get('gst_amount', 0):,.2f}\n"
        f"------------------------------------\n"
        f" *Grand Total Paid: Rs.{receipt_data.get('grand_total', 0):,.2f}*\n"
        f"------------------------------------\n"
        f" Location: Navrangpura, Ahmedabad\n"
        f" Reception: +91 9825012345\n\n"
        f"We look forward to styling you again soon! "
    )

    encoded_msg = urllib.parse.quote(msg)
    return f"https://wa.me/{phone}?text={encoded_msg}"


def generate_appointment_whatsapp_link(apt_data: dict) -> str:
    """Builds a WhatsApp confirmation URL for advance salon bookings."""
    phone = format_phone_for_whatsapp(apt_data.get("client_phone", ""))
    
    msg = (
        f" *GLORENZA SALON - APPOINTMENT CONFIRMED*\n"
        f"------------------------------------\n"
        f"Dear *{apt_data.get('client_name')}*,\n"
        f"Your salon appointment has been reserved!\n\n"
        f" *Booking Ref:* {apt_data.get('appointment_code')}\n"
        f" *Service:* {apt_data.get('service_name')}\n"
        f" *Specialist:* {apt_data.get('stylist_name')}\n"
        f" *Date:* {apt_data.get('date')}\n"
        f" *Time Slot:* {apt_data.get('time')}\n"
        f" *Station:* {apt_data.get('station', 'Styling Studio')}\n"
        f"------------------------------------\n"
        f" Navrangpura, Ahmedabad |  +91 9825012345\n\n"
        f"Please arrive 10 minutes prior to your scheduled slot. See you soon! "
    )

    encoded_msg = urllib.parse.quote(msg)
    return f"https://wa.me/{phone}?text={encoded_msg}"