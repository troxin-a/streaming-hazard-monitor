// Every load test device sends one reading per second, so the rate equals the number of sending devices.
// Run:
//   python -m scripts.create_load_devices --count 8800
//   restart receiver and detector: they load the devices at the start
//   k6 run -e RATE=750 scripts/k6-test.js    (the first 750 devices send; without RATE all of them do)
//   k6 run -e RATE=750 -e CHATTER=1 scripts/k6-test.js    (the readings are noisy around the threshold)
import {check} from 'k6';
import exec from 'k6/execution';
import http from 'k6/http';

const URL = 'http://127.0.0.1:8001/receiver/telemetry/';
const allKeys = JSON.parse(open('./k6-keys.json'));
const rate = Number(__ENV.RATE || allKeys.length);
if (rate > allKeys.length) {
    throw new Error(`RATE ${rate} needs ${rate} devices, only ${allKeys.length} are created`);
}
const keys = allKeys.slice(0, rate);

// Load test devices are CO sensors, the default threshold of their level 1 is 20 ppm.
const NORMAL_VALUE = 10; // With the noise the readings stay below the threshold: the level never changes.
const THRESHOLD = 20; // With the noise about a half of the readings is above the threshold: the level keeps changing.
const NOISE = 1; // Every reading differs from the base value by up to this number.
const baseValue = __ENV.CHATTER ? THRESHOLD : NORMAL_VALUE;

export const options = {
    scenarios: {
        telemetry: {
            executor: 'constant-arrival-rate', // k6 starts a fixed number of iterations over a specified period of time
            duration: '1m', // Total scenario duration
            rate: keys.length, // Number of iterations to start during each timeUnit period.
            preAllocatedVUs: keys.length, // Number of VUs to pre-allocate before test start to preserve runtime resources.
            timeUnit: '1s', // Period of time to apply the rate value.
        },
    },
};

export default function () {
    const key = keys[exec.scenario.iterationInTest % keys.length]; // Devices take turns: each one sends once per second.
    const value = baseValue + (Math.random() * 2 - 1) * NOISE;
    const body = JSON.stringify({value: Number(value.toFixed(3))}); // The receiver accepts up to 3 decimal places.
    const params = {headers: {'Content-Type': 'application/json', 'X-API-Key': key}, timeout: '1s'};
    const response = http.post(URL, body, params);
    check(response, {'status 202': (r) => r.status === 202});
}
