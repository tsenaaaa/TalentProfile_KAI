from datetime import datetime
import pandas as pd

class DateFormatter:
    @staticmethod
    def format_date(date_input, output_format="%d %B %Y"):
        """
        Menerima input berupa datetime, timestamp, atau string tanggal.
        Mengembalikan string dengan format seragam.
        """
        if pd.isna(date_input) or str(date_input).strip() == "":
            return "-"

        # Jika datetime atau pandas Timestamp
        if isinstance(date_input, (datetime, pd.Timestamp)):
            return date_input.strftime(output_format)

        # Jika string
        date_str = str(date_input).strip()

        # Coba parsing berbagai kemungkinan format
        possible_formats = [
            "%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d", "%d %B %Y", "%d %b %Y"
        ]
        for fmt in possible_formats:
            try:
                dt = datetime.strptime(date_str, fmt)
                return dt.strftime(output_format)
            except:
                continue

        # Jika gagal parsing, kembalikan string mentah
        return date_str
