import random

from django.core.management.base import BaseCommand
from faker import Faker

from main_app.models import Report

fake = Faker("id_ID")


class Command(BaseCommand):
    help = "Generate fake reports"

    def add_arguments(self, parser):
        parser.add_argument("num_records", type=int)

    def handle(self, *args, **kwargs):
        num_records = kwargs["num_records"]

        categories = {
            "Jalan Rusak": {
                "titles": [
                    "Jalan berlubang membahayakan pengendara",
                    "Aspal rusak di ruas jalan utama",
                    "Permukaan jalan retak dan tidak rata",
                    "Lubang besar di jalan lingkungan warga",
                ],
                "descriptions": [
                    "Terdapat kerusakan jalan yang cukup parah dan berisiko menyebabkan kecelakaan, terutama saat malam hari atau ketika hujan.",
                    "Kondisi jalan berlubang membuat kendaraan harus melambat mendadak dan mengganggu kelancaran lalu lintas di sekitar lokasi.",
                    "Warga berharap perbaikan segera dilakukan karena kerusakan jalan sudah berlangsung beberapa waktu dan semakin melebar.",
                ],
            },
            "Sampah": {
                "titles": [
                    "Tumpukan sampah belum diangkut",
                    "Sampah menumpuk di pinggir jalan",
                    "Area permukiman terganggu oleh sampah",
                    "Bau tidak sedap dari tumpukan sampah warga",
                ],
                "descriptions": [
                    "Sampah rumah tangga menumpuk di lokasi dan menimbulkan bau yang mengganggu aktivitas warga sekitar.",
                    "Kondisi kebersihan di area tersebut menurun karena sampah belum diangkut dalam beberapa hari terakhir.",
                    "Warga meminta penanganan lebih cepat agar lingkungan tetap bersih dan tidak menimbulkan masalah kesehatan.",
                ],
            },
            "Lampu Mati": {
                "titles": [
                    "Lampu jalan padam pada malam hari",
                    "Penerangan jalan tidak berfungsi",
                    "Beberapa titik lampu jalan mati",
                    "Jalan lingkungan gelap karena lampu rusak",
                ],
                "descriptions": [
                    "Lampu penerangan jalan di lokasi tidak menyala sehingga kondisi sekitar menjadi gelap dan rawan bagi pengguna jalan.",
                    "Kurangnya pencahayaan membuat warga merasa tidak aman saat melintas pada malam hari.",
                    "Diperlukan pengecekan dan perbaikan agar penerangan jalan kembali berfungsi dengan baik.",
                ],
            },
            "Drainase": {
                "titles": [
                    "Saluran drainase tersumbat",
                    "Drainase tidak mengalir dengan baik",
                    "Genangan muncul akibat saluran tersumbat",
                    "Parit lingkungan perlu dibersihkan",
                ],
                "descriptions": [
                    "Saluran air di sekitar lokasi tersumbat sehingga aliran tidak lancar dan berpotensi menyebabkan genangan saat hujan.",
                    "Warga melaporkan kondisi drainase yang kotor dan membutuhkan pembersihan agar tidak menimbulkan banjir kecil.",
                    "Penanganan diperlukan untuk memperlancar aliran air dan menjaga kebersihan lingkungan sekitar.",
                ],
            },
            "Keamanan": {
                "titles": [
                    "Area lingkungan minim pengawasan",
                    "Warga melaporkan gangguan keamanan",
                    "Situasi lingkungan dinilai kurang aman",
                    "Diperlukan perhatian pada keamanan wilayah",
                ],
                "descriptions": [
                    "Warga menyampaikan adanya kondisi yang membuat lingkungan terasa kurang aman, terutama pada jam-jam sepi.",
                    "Laporan ini diajukan agar pihak terkait dapat meningkatkan pengawasan dan tindak lanjut di area tersebut.",
                    "Diperlukan koordinasi lebih lanjut untuk memastikan keamanan dan kenyamanan warga sekitar tetap terjaga.",
                ],
            },
        }
        status_choices = ["REPORTED", "VERIFIED", "IN_PROGRESS", "RESOLVED"]
        street_names = [
            "Jl. Sudirman",
            "Jl. Diponegoro",
            "Jl. Ahmad Yani",
            "Jl. Kartini",
            "Jl. Gatot Subroto",
            "Jl. Pahlawan",
            "Jl. Melati",
            "Jl. Mawar",
            "Jl. Cendana",
            "Jl. Merdeka",
        ]
        districts = [
            "Tanjung Karang",
            "Kemiling",
            "Rajabasa",
            "Sukarame",
            "Panjang",
            "Teluk Betung",
            "Kedaton",
            "Way Halim",
            "Sukabumi",
            "Labuhan Ratu",
        ]

        category_names = list(categories.keys())

        for _ in range(num_records):
            category = random.choice(category_names)
            category_content = categories[category]

            Report.objects.create(
                title=random.choice(category_content["titles"]),
                category=category,
                description=random.choice(category_content["descriptions"]),
                location=(
                    f"{random.choice(street_names)} No. {random.randint(1, 250)}, "
                    f"Kec. {random.choice(districts)}, Bandar Lampung"
                ),
                status=random.choice(status_choices),
            )

        self.stdout.write(self.style.SUCCESS(f"{num_records} data berhasil dibuat!"))
