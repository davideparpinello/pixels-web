var express = require('express');
var app = express();
var path = require('path')
var fs = require("fs")
var formidable = require('formidable')
var readChunk = require('read-chunk')
const FileType = require('file-type')
const imagesFolder = path.join(__dirname, "public/img");

function populateDB() {
    var imagesDB = [];
    var i = 1;
    fs.readdir(imagesFolder, function (err, files) {
        //handling error
        if (err) {
            return console.log('Unable to scan directory: ' + err);
        }
        //listing all files using forEach
        files.forEach(function (file) {
            var image = {}
            image.ID = i++;
            image.path = "img/" + file
            imagesDB.push(image);
        });

        fs.writeFileSync('images.json', JSON.stringify(imagesDB), 'utf-8');

    });
}

populateDB();

app.set('view engine', 'ejs')
let imagesFile = fs.readFileSync('images.json')
let imagesDB = JSON.parse(imagesFile);

app.use(express.static('public'))
app.use('/uploads', express.static('public/img'));

app.get('/', function (req, res) {
    res.render('pages/index', {
        imagesDB
    }); //passiamo il databse immagini
});

app.post('/upload_photos', function (req, res) {
    var photos = [],
        form = new formidable.IncomingForm();

    // Tells formidable that there will be multiple files sent.
    form.multiples = true;
    // Upload directory for the images
    form.uploadDir = path.join(__dirname, 'tmp_uploads');

    // Invoked when a file has finished uploading.
    form.on('file', function (name, file) {


        var buffer = null,
            type = null,
            filename = '';

        // Read a chunk of the file.
        buffer = readChunk.sync(file.path, 0, 260);
        // Get the file type using the buffer read using read-chunk

        FileType.fromBuffer(buffer).then(function (type) {
            // Check the file type, must be either png,jpg or jpeg
            if (type !== null && (type.ext === 'png' || type.ext === 'jpg' || type.ext === 'jpeg')) {
                // Assign new file name
                filename = Date.now() + '-' + file.name;
                // Move the file with the new file name
                fs.rename(file.path, path.join(__dirname, 'public/img/' + filename), function () { });

                // Add to the list of photos
                photos.push({
                    status: true,
                    filename: filename,
                    type: type.ext,
                    publicPath: 'uploads/' + filename
                });
                console.log("upload");
            } else {
                photos.push({
                    status: false,
                    filename: file.name,
                    message: 'Invalid file type'
                });
                fs.unlink(file.path);
            }
        });


    });

    form.on('error', function (err) {
        console.log('Error occurred during processing - ' + err);
    });

    // Invoked when all the fields have been processed.
    form.on('end', function () {
        console.log('All the request fields have been processed.');
    });

    // Parse the incoming form fields.
    form.parse(req, function (err, fields, files) {
        res.status(200).json(photos);
    });
});

app.listen(3000, function () {
    console.log('Pixels web app listening on port 3000!');
});