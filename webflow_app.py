from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.filechooser import FileChooserIconView
from kivy.uix.image import Image
import requests
import os

# ======= CONFIG =======
API_TOKEN = "2bcb125f31b2c0c4c06a9b043d6dc144a0b8b5f7103a35c10cad63b2b7e5e0f0"
COLLECTION_ID = "68b327d9f1de8a0e3f730c33"
BASE_URL = "https://api.webflow.com/v2"
headers = {
    "Authorization": f"Bearer {API_TOKEN}",
    "accept": "application/json",
    "content-type": "application/json"
}

# Cloudinary
CLOUD_NAME = "daj5cu840"
UPLOAD_PRESET = "webflow"

def upload_image(file_path):
    url = f"https://api.cloudinary.com/v1_1/{CLOUD_NAME}/image/upload"
    with open(file_path, "rb") as f:
        data = {"upload_preset": UPLOAD_PRESET}
        files = {"file": f}
        res = requests.post(url, data=data, files=files).json()
        return res.get("secure_url")

class MainLayout(BoxLayout):
    item_id = None
    img_paths = {"img1": None, "img2": None, "img3": None}

    # Load item pertama
    def load_items(self):
        url = f"{BASE_URL}/collections/{COLLECTION_ID}/items"
        res = requests.get(url, headers=headers).json()
        items = res.get("items", [])
        if items:
            item = items[0]
            self.item_id = item["id"]
            fd = item["fieldData"]
            # isi field
            self.ids.name.text = fd.get("name", "")
            self.ids.slug.text = fd.get("slug", "")
            self.ids.color.text = fd.get("color", "")
            self.ids.size.text = fd.get("size", "")
            self.ids.price.text = fd.get("price", "")
            self.ids.kota.text = fd.get("kota", "")
            self.ids.deskripsi.text = fd.get("deskripsi", "")
            self.ids.pengirim.text = fd.get("pengirim", "")
            self.ids.linkrintisan.text = fd.get("linkrintisan", "")
            # update preview gambar
            for i in ["img1","img2","img3"]:
                url = fd.get(i, {}).get("url") if isinstance(fd.get(i), dict) else fd.get(i)
                self.ids[f"{i}_label"].text = url if url else "Belum ada file"
                if url:
                    self.ids[f"{i}_preview"].source = url
            self.ids.status.text = f"Item '{fd.get('name')}' berhasil diload"
        else:
            self.ids.status.text = "Tidak ada item"

    # Pilih file gambar
    def choose_file(self, img_field):
        filechooser = FileChooserIconView(filters=["*.png","*.jpg","*.jpeg"])
        popup = Popup(title="Pilih Gambar", content=filechooser, size_hint=(0.9,0.9))

        def select_file(instance, selection):
            if selection:
                self.img_paths[img_field] = selection[0]
                self.ids[f"{img_field}_label"].text = os.path.basename(selection[0])
                self.ids[f"{img_field}_preview"].source = selection[0]
                popup.dismiss()

        filechooser.bind(on_submit=select_file)
        popup.open()

    # Update item
    def update_item(self):
        if not self.item_id:
            self.ids.status.text = "Load item dulu!"
            return

        # Upload gambar
        image_urls = {}
        for img_field in ["img1","img2","img3"]:
            path = self.img_paths[img_field]
            if path:
                self.ids.status.text = f"Uploading {img_field}..."
                url = upload_image(path)
                image_urls[img_field] = url

        # Payload
        data = {
            "isArchived": False,
            "isDraft": False,
            "fieldData": {
                "name": self.ids.name.text,
                "slug": self.ids.slug.text,
                "color": self.ids.color.text,
                "size": self.ids.size.text,
                "price": self.ids.price.text,
                "kota": self.ids.kota.text,
                "deskripsi": self.ids.deskripsi.text,
                "pengirim": self.ids.pengirim.text,
                "linkrintisan": self.ids.linkrintisan.text,
            }
        }

        data["fieldData"].update(image_urls)

        url = f"{BASE_URL}/collections/{COLLECTION_ID}/items/{self.item_id}/live"
        res = requests.patch(url, headers=headers, json=data)
        if res.status_code == 200:
            self.ids.status.text = "Item berhasil diupdate!"
        else:
            self.ids.status.text = f"Gagal update ({res.status_code})"

class WebflowApp(App):
    def build(self):
        return MainLayout()

if __name__ == "__main__":
    WebflowApp().run()
