// Isolated localhost browser gate. No real health information or provider requests.
const { chromium } = require(process.env.ZINC_PLAYWRIGHT_PATH || 'playwright');
const fs = require('node:fs/promises');
const path = require('node:path');
const assert = require('node:assert/strict');
const base = process.env.ZINC_TEST_URL || 'http://127.0.0.1:8504';
const out = path.resolve(__dirname, '../verification/browser');
async function main() {
  await fs.mkdir(out, {recursive:true});
  const browser = await chromium.launch({headless:true});
  const results=[];
  try {
    for (const viewport of [{width:1280,height:900},{width:390,height:844}]) {
      const kind = viewport.width===390?'phone':'desktop';
      const context=await browser.newContext({viewport, reducedMotion: 'reduce', acceptDownloads:true});
      const page=await context.newPage();
      const capture = async name => {
        await page.getByTestId('stMain').evaluate(el=>el.scrollTo(0,0));
        await page.screenshot({path:path.join(out,kind+'-'+name+'.png'),fullPage:true});
      };
      const errors=[];
      page.on('pageerror', e=>errors.push(e.message));
      await page.goto(base);
      const button = name=>page.getByRole('button',{name,exact:true});
      const waitHeading = name=>page.getByRole('heading',{name,exact:true}).waitFor({state:'visible'});
      const navigate = async name=>{
        await page.getByText(name,{exact:true}).click();
        await waitHeading({'Your week':'Your week, all four sections.','Train':'One activity at a time.','Coach':'Guidance for your whole week.','Progress':'Progress','Overview':'Your complete week, Maria.'}[name]);
      };
      if(kind==='phone')await page.getByTestId('stExpandSidebarButton').click();
      await button('Load Maria').click();
      if(kind==='phone')await page.getByTestId('stSidebarCollapseButton').click();
      await page.getByText('I am using fictional information for this prototype.',{exact:true}).click();
      await button('Continue to safety').click();
      await waitHeading('Before we make a plan');
      await button('Continue to focus').click();
      const alert = page.getByTestId('stAlert');
      await alert.waitFor();
      assert.equal(await alert.locator('p').first().evaluate(el=>getComputedStyle(el).color),'rgb(18, 54, 91)');
      const answers=page.getByRole('radio',{name:'No',exact:true});
      await answers.first().waitFor({state:'attached'});
      assert.equal(await answers.count(),7);
      for(let i=0;i<7;i++)await page.getByText('No',{exact:true}).nth(i).click();
      await button('Continue to focus').click();
      await page.getByRole('checkbox',{name:'Extra yoga',exact:true}).waitFor();
      assert.equal(await page.getByRole('checkbox',{name:'Extra yoga',exact:true}).isChecked(),false);
      await button('Create my complete week').click();
      await waitHeading('Your complete week, Maria.');
      for(const section of ['Strength & balance','Yoga','Brain games','Relaxation'])assert(await page.getByText(section,{exact:false}).count()>0);
      await capture('overview');
      // Keyboard navigation is retained in the real browser, with a visible focus style.
      await button('Explore my week').focus();
      await page.keyboard.press('Enter');
      await waitHeading('Your week, all four sections.');
      assert(await page.getByRole('heading',{name:/Strength & balance/}).count()>0);
      await capture('week');
      // Start a real strength activity and submit exactly one set, then end it as partial.
      await button('Start activity').first().click();
      await waitHeading('One activity at a time.');
      await button('Done set').click();
      await page.getByText(/Set 2 of 2/).waitFor();
      await capture('strength');
      await page.getByRole('button',{name:'Done set',exact:true}).scrollIntoViewIfNeeded();
      await page.screenshot({path:path.join(out,kind+'-strength-form.png')});
      await button('Skip / end this activity').click();
      await page.getByText('Activity ended: partial.',{exact:true}).waitFor();
      await navigate('Your week');
      // Remaining Start activity controls are brain, relaxation, yoga, strength, etc.
      await button('Start activity').first().click();
      await page.getByRole('spinbutton',{name:'Next number',exact:true}).waitFor();
      await page.getByRole('spinbutton',{name:'Next number',exact:true}).fill('9');
      await button('Check answer').click();
      await page.getByText(/Puzzle 2 of 5/).waitFor();
      await capture('brain');
      const feedback=page.getByTestId('stAlert');
      assert.equal(await feedback.locator('p').first().evaluate(el=>getComputedStyle(el).color),'rgb(18, 54, 91)');
      assert.equal(await feedback.evaluate(el=>getComputedStyle(el).backgroundColor),'rgb(242, 248, 255)');
      await button('Skip / end this activity').click();
      await page.getByText('Activity ended: partial.',{exact:true}).waitFor();
      await navigate('Your week');
      await button('Start activity').first().click();
      await page.getByText('5 minutes',{exact:true}).waitFor();
      await page.getByText('5 minutes',{exact:true}).click();
      const circle=page.locator('.breath-circle');
      await circle.waitFor();
      const motion=await circle.evaluate(el=>getComputedStyle(el).animationName);
      assert.equal(motion,'none');
      assert.equal(await page.getByText('5 minutes',{exact:true}).evaluate(el=>getComputedStyle(el).color),'rgb(237, 247, 255)');
      await page.emulateMedia({reducedMotion:'no-preference'});
      assert.equal(await circle.evaluate(el=>getComputedStyle(el).animationDuration),'10s');
      for (const [time,word] of [[2500,'Breathe in'],[7500,'Breathe out']]) {
        const phase = await circle.evaluate((el,t)=>{for(const a of el.getAnimations({subtree:true})){a.pause();a.currentTime=t;} return getComputedStyle(el,'::after').content;},time);
        assert(phase.includes(word));
      }
      await page.emulateMedia({reducedMotion:'reduce'});
      await capture('relaxation');
      await button('I completed my breathing practice').click();
      await page.getByText('Activity completed.',{exact:true}).waitFor();
      await navigate('Your week');
      await button('Start activity').first().click();
      await button('Done pose').waitFor();
      await button('Done pose').click();
      await page.getByText(/Pose 2 of 5/).waitFor();
      await capture('yoga');
      await button('Skip / end this activity').click();
      await page.getByText('Activity ended: partial.',{exact:true}).waitFor();
      await navigate('Progress');
      await page.getByText('Relaxation: 5 self-reported minutes',{exact:true}).waitFor();
      await capture('progress');
      await page.locator('.chart-panel').scrollIntoViewIfNeeded();
      await page.screenshot({path:path.join(out,kind+'-progress-chart.png')});
      const weekLabel = page.getByTestId('stWidgetLabel').filter({hasText:'Week'});
      assert.equal(await weekLabel.locator('p').evaluate(el=>getComputedStyle(el).color),'rgb(237, 247, 255)');
      await button('Export all demo history').scrollIntoViewIfNeeded();
      await page.screenshot({path:path.join(out,kind+'-progress-summary.png')});
      const downloadPromise=page.waitForEvent('download');
      await button('Export all demo history').click();
      const download=await downloadPromise;
      const target=path.join(out,kind+'-export.json');
      await download.saveAs(target);
      const data=JSON.parse(await fs.readFile(target,'utf8'));
      assert.equal(data.logs.sessions.length,1);
      assert.equal(Object.values(data.activity_sessions).length,4);
      assert.equal(Object.values(data.activity_sessions).find(a=>a.section==='relaxation').completed_minutes,5);
      await navigate('Overview');
      await button('Start next week').click();
      await page.getByText(/Protect · Week 2/).waitFor();
      await navigate('Progress');
      // Native Streamlit selectbox supports keyboard selection of the previous week.
      const week=page.getByRole('combobox',{name:'Week',exact:true});
      await week.click();
      await week.press('ArrowUp');
      await week.press('Enter');
      await page.getByText('Relaxation: 5 self-reported minutes',{exact:true}).waitFor();
      const overflow=await page.evaluate(()=>document.documentElement.scrollWidth>window.innerWidth);
      assert.equal(overflow,false,kind+' page overflow');
      assert.deepEqual(errors,[]);
      results.push({viewport,kind,pass:true,checks:['onboarding','all sections','keyboard navigation','set log','brain answer','yoga feedback','reduced motion','normal breathing keyframe phases','alert and option contrast','relaxation completion','progress','export JSON','week rollover','historical progress','no page errors','no horizontal page overflow']});
      await context.close();
    }
  } finally {await browser.close();}
  await fs.writeFile(path.join(out,'results.json'),JSON.stringify({time:new Date().toISOString(),url:base,results},null,2));
  console.log(JSON.stringify(results,null,2));
}
main().catch(e=>{console.error(e);process.exitCode=1;});
