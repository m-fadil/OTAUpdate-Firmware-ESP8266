const express = require('express');
const { networkInterfaces } = require('os');
const path = require('path');
 
const app = express();
const nets = networkInterfaces();
 
// Server port
const PORT = 3000;
 
app.get('/', (request, response) => response.send('Server on'));

let downloadCounter = 1;
app.get('/firmware/httpUpdateNew.bin', (request, response) => {
    response.download(path.join(__dirname, 'firmware/httpUpdateNew.bin'), 'httpUpdateNew.bin', (err)=>{
        if (err) {
            console.error("Problem on download firmware: ", err)
        }else{
            downloadCounter++;
        }
    });
    console.log('Your file has been downloaded '+downloadCounter+' times!')
})
 
app.listen(PORT, () => {
    console.log('Server download bin menyala!')
});