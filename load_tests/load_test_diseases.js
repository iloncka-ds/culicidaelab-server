// Load Testing is a type of Performance Testing used to determine a system's behavior under both normal and peak conditions.

// Load Testing is used to ensure that the application performs satisfactorily when many users access it at the same time.

// You should run a Load Test to:

//   - Assess the current performance of your system under typical and peak load.
//   - Make sure you continue to meet the performance standards as you make changes to your system (code and infrastructure).

import http from 'k6/http';
import { htmlReport } from "https://raw.githubusercontent.com/benc-uk/k6-reporter/main/dist/bundle.js";
import { check, sleep } from 'k6';


export const options = {


    stages: [

        { duration: '5m', target: 60 }, // simulate ramp-up of traffic from 1 to 60 users over 5 minutes.
        { duration: '10m', target: 60 }, // stay at 60 users for 10 minutes
        { duration: '3m', target: 100 }, // ramp-up to 100 users over 3 minutes (peak hour starts)
        { duration: '2m', target: 100 }, // stay at 100 users for short amount of time (peak hour)
        { duration: '3m', target: 60 }, // ramp-down to 60 users over 3 minutes (peak hour ends)
        { duration: '10m', target: 60 }, // continue at 60 for additional 10 minutes
        { duration: '5m', target: 0 }, // ramp-down to 0 users

      ],

      thresholds: {

        http_req_duration: ['p(99)<1500'], // 99% of requests must complete below 1.5s

      },
};



export default function () {

    const res = http.get('http://127.0.0.1:8000/api/diseases?limit=10');

    check(res, { 'status was 200': (r) => r.status == 200 });

    sleep(1);

}
export function handleSummary(data) {
        return {
        "summary_load_test_diseases.html": htmlReport(data),
        };
    }
