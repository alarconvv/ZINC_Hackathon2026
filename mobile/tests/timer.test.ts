import {test} from 'node:test';
import assert from 'node:assert/strict';
import {elapsedSeconds} from '../src/timer.ts';
test('home timers use real elapsed time across backgrounding and stop at 30 seconds',()=>{assert.equal(elapsedSeconds(1000,500),0);assert.equal(elapsedSeconds(1000,10999),9);assert.equal(elapsedSeconds(1000,31000),30);assert.equal(elapsedSeconds(1000,90000),30);});
