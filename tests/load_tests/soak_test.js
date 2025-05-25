// A soak test uncovers performance and reliability issues stemming from a system being under pressure for an extended period.

// Reliability issues typically relate to bugs, memory leaks, insufficient storage quotas, incorrect configuration or infrastructure failures. Performance issues typically relate to incorrect database tuning, memory leaks, resource leaks or a large amount of data.

// With a soak test you can simulate days worth of traffic in only a few hours.

// You typically run this test to:

//     - Verify that your system doesn't suffer from bugs or memory leaks, which result in a crash or restart after several hours of operation.
//     - Verify that expected application restarts don't lose requests.
//     - Find bugs related to race-conditions that appear sporadically.
//     - Make sure your database doesn't exhaust the allotted storage space and stops.
//     - Make sure your logs don't exhaust the allotted disk storage.
//     - Make sure the external services you depend on don't stop working after a certain amount of requests are executed.

// It is recommended to configure your soak test at about 80% capacity
// of your system. If your system can handle a maximum of 500 simultaneous users,
// you should configure your soak test to 400 VUs.

import http from 'k6/http';
import { htmlReport } from "https://raw.githubusercontent.com/benc-uk/k6-reporter/main/dist/bundle.js";
import { check, sleep } from 'k6';


export const options = {

    stages: [

        { duration: '2m', target: 400 }, // ramp up to 400 users
        { duration: '1h26m', target: 400 }, // stay at 400 for ~4 hours
        { duration: '2m', target: 0 }, // scale down. (optional)
    ],

};


// for (let id = 1; id <= 100; id++) {
//     http.get(`http://localhost:8001/item/${id}?k=3`, {
//       tags: { name: 'PostsItemURL' },
//     });
//   }

export default function () {

    const res = http.get('http://127.0.0.1:8000/api/filter_options');

    check(res, { 'status was 200': (r) => r.status == 200 });

    sleep(1);

}
export function handleSummary(data) {
        return {
        "summary_soak_test.html": htmlReport(data),
        };
    }
