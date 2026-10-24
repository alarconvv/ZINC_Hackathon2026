import {test} from 'node:test';
import assert from 'node:assert/strict';
import {reminderSchedule} from '../src/reminderSchedule.ts';
test('native weekly triggers follow server days and chosen local time',()=>{
 assert.deepEqual(reminderSchedule('09:30',['Mon','Thu']),[{day:'Mon',weekday:2,hour:9,minute:30},{day:'Thu',weekday:5,hour:9,minute:30}]);
 assert.equal(reminderSchedule('23:59',['Sun'])[0].weekday,1);
 for(const time of ['24:00','09:60','9am'])assert.throws(()=>reminderSchedule(time,['Mon']));
 assert.throws(()=>reminderSchedule('09:00',['Invalid']));
});
