const mqtt = require("mqtt");

const protocol = 'mqtt'
const host = "mqtt.eclipseprojects.io"
const port = '1883'
const topic = ["klien_cekESP",]
const clientId = `mqtt_${Math.random().toString(16).slice(3)}`
const connectUrl = `${protocol}://${host}:${port}`

const client = mqtt.connect(connectUrl, {
    clientId: clientId,
    connectTimeout: 4000,
    reconnectPeriod: 1000,
})
  
client.on('connect', () => {
    console.log('Connected')
    client.subscribe(topic, () => {
        console.log(`Subscribe to topic '${topic}'`)
    })
    const print = setInterval(() => {
        client.publish(topic[0], 'tes')
    }, 1000)
})

client.on('message', (topic, message) => {
    // message is a Buffer
    let strMessage = message.toString();
    // let objMessage = JSON.parse(strMessage);
    console.log(strMessage);
})
