const express = require("express");
const multer = require('multer');
const path = require("path");
const fs = require("fs")

const app = express();
const PORT = 3000;

const storage = multer.diskStorage({
    destination: function (req, file, cb) {
        cb(null, "firmware/");
    },
    filename: function (req, file, cb) {
        cb(null, "firmware_update.bin");
    },
});

const upload = multer({
    storage: storage,
    overwrite: true,
});

app.get("/", (request, response) => response.send("Server on"));

app.post("/upload", upload.single("file"), (req, res) => {
    const allowedExtensions = [".bin"];
    const fileExtension = req.file.originalname.split(".").pop();

    if (!allowedExtensions.includes(`.${fileExtension}`)) {
        fs.unlinkSync(req.file.path);

        return res.status(400).send("Ekstensi file tidak didukung");
    }
    res.send("File berhasil diunggah");
});

app.get("/firmware/firmware_update.bin", (request, response) => {
    response.download(path.join(__dirname, "firmware/firmware_update.bin"), "firmware_update.bin", (err) => {
        if (err) {
            console.error("Problem on download firmware: ", err);
        }
    });
});

app.listen(PORT, () => {
    console.log("Server download bin menyala!");
});
