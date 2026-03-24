import axios from 'axios';

// Base URL for CasaPAT API
const domain = window.location.hostname.trim()
export const BASE_URL = domain.includes('tail') ? 'http://pat.tailf035ad.ts.net:5000' : 'http://pat.local:5000';

/**
 * Make a GET request to the CasaPAT API
 * @param {string} route - API route (e.g., '/air/devices')
 * @returns {Promise} Axios response promise
 */
export const apiRequestGet = (route) => {
  return axios.get(`${BASE_URL}${route}`, {
    headers: {
      'Content-Type': 'application/json',
    },
    timeout: 10000,
  });
};

/**
 * Make a POST request to the CasaPAT API
 * @param {string} route - API route
 * @param {Object} body - Request body
 * @returns {Promise} Axios response promise
 */
export const apiRequestPost = (route, body) => {
  return axios.post(`${BASE_URL}${route}`, body, {
    headers: {
      'Content-Type': 'application/json',
    },
    timeout: 10000,
  });
};

/**
 * Make a PUT request to the CasaPAT API
 * @param {string} route - API route
 * @param {Object} body - Request body
 * @returns {Promise} Axios response promise
 */
export const apiRequestPut = (route, body) => {
  return axios.put(`${BASE_URL}${route}`, body, {
    headers: {
      'Content-Type': 'application/json',
    },
    timeout: 10000,
  });
};

/**
 * Make a DELETE request to the CasaPAT API
 * @param {string} route - API route
 * @returns {Promise} Axios response promise
 */
export const apiRequestDelete = (route) => {
  return axios.delete(`${BASE_URL}${route}`, {
    headers: {
      'Content-Type': 'application/json',
    },
    timeout: 10000,
  });
};

