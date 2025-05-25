import http from 'k6/http';
import { htmlReport } from "https://raw.githubusercontent.com/benc-uk/k6-reporter/main/dist/bundle.js";
import { check, sleep } from 'k6';


export const options = {

    stages: [

        { duration: '30s', target: 20 },

        { duration: '1m30s', target: 10 },

        { duration: '20s', target: 0 },

    ],

};


export default function () {

    const res = http.get('http://127.0.0.1:8000/api/filter_options');

    check(res, { 'status was 200': (r) => r.status == 200 });

    sleep(1);

}
export function handleSummary(data) {
        return {
        "summary_simple_test.html": htmlReport(data),
        };
    }
