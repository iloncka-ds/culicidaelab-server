// You typically want to stress test an API or website to determine:

//     - How your system will behave under extreme conditions.
//     - What the maximum capacity of your system is in terms of users or throughput.
//     - The breaking point of your system and its failure mode.
//     - If your system will recover without manual intervention after the stress test is over.

import http from 'k6/http';
import { htmlReport } from "https://raw.githubusercontent.com/benc-uk/k6-reporter/main/dist/bundle.js";
import { check, sleep } from 'k6';


export const options = {

    insecureSkipTLSVerify: true,
    noConnectionReuse: false,

    stages: [
        { duration: '2m', target: 100 }, // below normal load
        { duration: '2m', target: 200 }, // normal load
        { duration: '2m', target: 300 }, // around the breaking point
        { duration: '2m', target: 400 }, // beyond the breaking point
        { duration: '5m', target: 0 }, // scale down. Recovery stage.
        ],

};



export default function () {

    const res = http.get('http://127.0.0.1:8000/api/filter_options');

    check(res, { 'status was 200': (r) => r.status == 200 });

    sleep(1);

}
export function handleSummary(data) {
        return {
        "load_tests/summary_stress_test_filter_options.html": htmlReport(data),
        };
    }
