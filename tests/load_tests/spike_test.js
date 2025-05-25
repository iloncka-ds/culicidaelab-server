// You want to execute a spike test to determine:

//     - How your system will perform under a sudden surge of traffic.
//     - If your system will recover once the traffic has subsided.

import http from 'k6/http';
import { htmlReport } from "https://raw.githubusercontent.com/benc-uk/k6-reporter/main/dist/bundle.js";
import { check, sleep } from 'k6';


export const options = {

    stages: [
        { duration: '10s', target: 100 }, // below normal load
        { duration: '1m', target: 100 },
        { duration: '10s', target: 1400 }, // spike to 1400 users
        { duration: '3m', target: 1400 }, // stay at 1400 for 3 minutes
        { duration: '10s', target: 100 }, // scale down. Recovery stage.
        { duration: '3m', target: 100 },
        { duration: '10s', target: 0 },
        ],

};



export default function () {

    const res = http.get('http://127.0.0.1:8000/api/filter_options');

    check(res, { 'status was 200': (r) => r.status == 200 });

    sleep(1);

}
export function handleSummary(data) {
        return {
        "summary_spike_test.html": htmlReport(data),
        };
    }
