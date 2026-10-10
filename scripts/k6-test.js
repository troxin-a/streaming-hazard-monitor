// Run:
//   python -m scripts.create_load_devices
//   k6 run -e RATE=750 scripts/k6-test.js
import {check} from 'k6';
import http from 'k6/http';

const URL = 'http://127.0.0.1:8001/receiver/telemetry/';
const keys = JSON.parse(open('./k6-keys.json'));

export const options = {
    scenarios: {
        telemetry: {
            executor: 'constant-arrival-rate', // k6 starts a fixed number of iterations over a specified period of time
            duration: '1m', // Total scenario duration
            rate: Number(__ENV.RATE), // Number of iterations to start during each timeUnit period.
            preAllocatedVUs: Number(__ENV.RATE), // Number of VUs to pre-allocate before test start to preserve runtime resources.
            timeUnit: '1s', // Period of time to apply the rate value.
        },
    },
};

export default function () {
    const key = keys[Math.floor(Math.random() * keys.length)];
    const body = JSON.stringify({value: 42.5});
    const params = {headers: {'Content-Type': 'application/json', 'X-API-Key': key}, timeout: '1s'};
    const response = http.post(URL, body, params);
    check(response, {'status 202': (r) => r.status === 202});
}
