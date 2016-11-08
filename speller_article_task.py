
#######################
# SSVEP Training Task #
#######################

#   ver 0.1 mbod@asc.upenn.edu 11/6/16
#


from __future__ import print_function, division

from psychopy import core, event, logging, visual, gui, data

import datetime
import sys
import os
import random
import string
import pandas as pd
import numpy as np



##########
# params #
##########

use_fullscreen=False
DEBUG = False

total_sessions = 20       # 20 days of training - 5 days x 4 weeks
articles_per_session = 8

timing = {
    'instruct1': 2.0,
    'read_article': 18.0
}

standard_words = [
    'cat',
    'zebra',
    'banana',
    'lazy brown fox'
]


############################
# GUI input session params #
############################
info = {
        'Session': range(1,total_sessions+1),
        'Subject ID': '',
        'Experimenter':'',}
infoDlg = gui.DlgFromDict(dictionary=info, title='SSVEP Experiment', 
    order=['Session', 'Subject ID', 'Experimenter'], 
    tip={'Experimenter': 'trained visual observer, initials'},
    )
if not infoDlg.OK: #this will be True (user hit OK) or False (cancelled)
    print('User Cancelled')
    sys.exit('Please enter details')


current_session = int(info['Session'])
subj_id = info['Subject ID']
stim_filename = os.path.join('stimuli','{}_stim.csv'.format(subj_id))
stim_exist = os.path.exists(stim_filename)

log_filename = os.path.join('logs','{}_sess{}.csv'.format(subj_id, current_session))

timestamp = datetime.datetime.strftime(datetime.datetime.now(),'%Y-%m-%d %H:%M')

# create a stimuli file for all sessions
# for this subject if current_session is 1 and
# now csv file for subject exists in stimuli folder
if current_session == 1 and not stim_exist:
    article_df = pd.read_csv('data/stimuli_articles_task.csv')
    
    # sample half social - half non-social
    aids = article_df.id
    social_ids = random.sample(aids,40)
    article_df['condition']=['share' if id in social_ids else 'nonshare' for id in aids]
    
    # 20 sessions - 10 social 10 non social
    sessions = ['share'] * 10 + ['nonshare'] * 10
    
    session_order = []
    while sessions:
        random.shuffle(sessions)
        sval = sessions.pop()
        if len(session_order)>=2:
            if session_order[-1]==sval and session_order[-2]==sval:
                sessions.append(sval)
                sval=None
        if sval != None:
            session_order.append(sval)
        
    sample_ids={'share':[], 'nonshare': []}
    
    session_data = []
    
    for sidx, session in enumerate(session_order):
        snum = sidx+1
        if not sample_ids[session]:
            sample_ids[session]=article_df[article_df.condition==session].id
        
        id_pool = sample_ids[session]
        aids = random.sample(id_pool, articles_per_session)
        sample_ids[session] = [id for id in sample_ids[session] if id not in aids]
        session_df=article_df[article_df.id.isin(aids)].copy()
        session_df['session']=snum
        session_data.append(session_df)
    
  

    ppt_stimuli=pd.concat(session_data)
    ppt_stimuli.to_csv(stim_filename, index=False)
else:
    ppt_stimuli = pd.read_csv(os.path.join('stimuli','{}_stim.csv'.format(subj_id)))

session_stimuli = ppt_stimuli[ppt_stimuli.session==current_session]
trials = data.TrialHandler(session_stimuli.to_dict(orient='record'),1)

# set up window
win = visual.Window([800,600], monitor="testMonitor", units="deg", fullscr=use_fullscreen, allowGUI=False)

# set up stimuli
headline = visual.TextStim(win, text='', pos=(0,5), wrapWidth=22, height=1.2)
abstract = visual.TextStim(win, text='', pos=(0,0), wrapWidth=22, height=1.1)

entry_instruction = visual.TextStim(win, text='', pos=(-3,4), height=0.8, wrapWidth=22)
end_message = visual.TextStim(win, text='Press [Enter] to end', height=0.6, pos=(0,-4))
text_entry_box = visual.Rect(win, pos=(0,0), width=18, height=5)
text_entry = visual.TextStim(win, text='', pos=(0,0), height=0.8, font='Courier' )

instruct1 = visual.TextStim(win, text='Please read the following article summary', height=0.8, wrapWidth=22)


#############
# FUNCTIONS #
#############

def run_speller():
    k=[None]
    text_string=''
    while k[0] not in ['return','q']:
        text_entry.setText(text_string)
        entry_instruction.draw()
        text_entry.draw()
        text_entry_box.draw()
        end_message.draw()
        win.flip()
        
        k=event.waitKeys()
        
        if k[0] in ['backspace','delete']:
           text_string=text_string[:-1]
        elif k[0] in string.letters or k[0]=='space':
           text_string=text_string+k[0].replace('space',' ')
           

    return text_string

############
#
# HERE WE CAN ADD THE STANDARD
# SPELLING OF WORDS/PHRASES 
#
#########


for word in standard_words:
    entry_instruction.setText('Please type: {}'.format(word.upper()))
    text_string = run_speller()


for trial in trials:
    headline.setText(trial['headline'])
    abstract.setText(trial['abstract'])
    
    
    entry_instruction_text = 'Share this article with your Twitter followers' if trial['condition']=='share' else 'Write the first few words of headline'
    entry_instruction.setText(entry_instruction_text)
    
    
    instruct1.draw()
    win.flip()
    core.wait(timing['instruct1'])
    
    headline.draw()
    abstract.draw()
    win.flip()
    core.wait(timing['read_article'])

    ############ 
    # THIS IS THE PLACE WHERE 
    # SPELLER INPUT CODE COULD BE INCORPORATED
    ############
    
    # - for now it takes keyboard input and logs input


    text_string = run_speller()
       
    
    # log text_string
    trials.addData('text_entry',text_string)
    if DEBUG:
        print(text_string)

for word in standard_words:
    entry_instruction.setText('Please type: {}'.format(word.upper()))
    text_string = run_speller()


####
# write out log

trials.saveAsText(log_filename, delim=',')
