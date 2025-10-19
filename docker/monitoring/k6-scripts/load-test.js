// K6 Load Testing Script for CulicidaeLab
// Tests API endpoints and frontend performance

import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend, Counter } from 'k6/metrics';

// Custom metrics
const errorRate = new Rate('error_rate');
const responseTime = new Trend('response_time');
const requestCount = new Counter('request_count');

// Test configuration
export const options = {
  stages: [
    { duration: '2m', target: 10 }, // Ramp up to 10 users
    { duration: '5m', target: 10 }, // Stay at 10 users
    { duration: '2m', target: 20 }, // Ramp up to 20 users
    { duration: '5m', target: 20 }, // Stay at 20 users
    { duration: '2m', target: 0 },  // Ramp down to 0 users
  ],
  thresholds: {
    http_req_duration: ['p(95)<2000'], // 95% of requests should be below 2s
    http_req_failed: ['rate<0.05'],    // Error rate should be below 5%
    error_rate: ['rate<0.05'],
  },
};

// Base URLs
const BASE_URL = __ENV.BASE_URL || 'http://nginx';
const API_BASE = `${BASE_URL}/api`;
const FRONTEND_BASE = BASE_URL;

// Test data
const testData = {
  healthCheck: `${API_BASE}/health`,
  frontend: FRONTEND_BASE,
  // Add more endpoints as needed
};

export default function () {
  // Test API health endpoint
  testHealthEndpoint();

  // Test frontend loading
  testFrontendLoading();

  // Add more test scenarios

  sleep(1);
}

function testHealthEndpoint() {
  const response = http.get(testData.healthCheck, {
    headers: {
      'Accept': 'application/json',
    },
    timeout: '30s',
  });

  const success = check(response, {
    'health check status is 200': (r) => r.status === 200,
    'health check response time < 1000ms': (r) => r.timings.duration < 1000,
    'health check has correct content-type': (r) =>
      r.headers['Content-Type'] && r.headers['Content-Type'].includes('application/json'),
  });

  // Record metrics
  errorRate.add(!success);
  responseTime.add(response.timings.duration);
  requestCount.add(1);
}

function testFrontendLoading() {
  const response = http.get(testData.frontend, {
    headers: {
      'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
      'User-Agent': 'K6 Load Test',
    },
    timeout: '30s',
  });

  const success = check(response, {
    'frontend status is 200': (r) => r.status === 200,
    'frontend response time < 3000ms': (r) => r.timings.duration < 3000,
    'frontend has HTML content': (r) =>
      r.headers['Content-Type'] && r.headers['Content-Type'].includes('text/html'),
  });

  // Record metrics
  errorRate.add(!success);
  responseTime.add(response.timings.duration);
  requestCount.add(1);
}

// Setup function - runs once before the test
export function setup() {
  console.log('Starting CulicidaeLab load test...');
  console.log(`Base URL: ${BASE_URL}`);

  // Verify services are available
  const healthResponse = http.get(testData.healthCheck);
  if (healthResponse.status !== 200) {
    throw new Error(`Health check failed: ${healthResponse.status}`);
  }

  return { startTime: new Date() };
}

// Teardown function - runs once after the test
export function teardown(data) {
  const endTime = new Date();
  const duration = (endTime - data.startTime) / 1000;
  console.log(`Load test completed in ${duration} seconds`);
}
