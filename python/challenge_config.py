##-----------------------------------------------------------------------------
##
## challenge specific code and configuration
##
##-----------------------------------------------------------------------------

import validation_helpers
import synapseclient
syn = synapseclient.login(silent=True)

## A Synapse project will hold the assetts for your challenge. Put its
## synapse ID here, for example
## CHALLENGE_SYN_ID = "syn1234567"
CHALLENGE_SYN_ID = "syn3157598"

## Name of your challenge, defaults to the name of the challenge's project
CHALLENGE_NAME = "NCI Up For A Challenge"

## Synapse user IDs of the challenge admins who will be notified by email
## about errors in the scoring script
ADMIN_USER_IDS = ["3323072", "2224171", "3323809"]

## Each question in your challenge should have an evaluation queue through
## which participants can submit their predictions or models. The queues
## should specify the challenge project as their content source. Queues
## can be created like so:
##   evaluation = syn.store(Evaluation(
##     name="My Challenge Q1",
##     description="Predict all the things!",
##     contentSource="syn1234567"))
## ...and found like this:
##   evaluations = list(syn.getEvaluationByContentSource('syn3375314'))
## Configuring them here as a list will save a round-trip to the server
## every time the script starts.
evaluation_queues = [
{u'contentSource': u'syn3157598',
 u'createdOn': u'2015-06-15T17:34:55.090Z',
 u'description': u'The goal of this Challenge is to use innovative approaches to identify novel pathways - including new genes or combinations of genes, genetic variants, or sets of genomic features - involved in breast cancer susceptibility in order to generate new biological hypotheses.',
 u'etag': u'fe52c239-58a0-4d79-b0f4-3348ac50e33f',
 u'id': u'4484862',
 u'name': u'NCI Up For a Challenge (U4C)',
 u'ownerId': u'3323072',
 u'quota': {u'firstRoundStart': u'2016-02-09T16:47:20.000Z',
  u'roundDurationMillis': 1,
  u'submissionLimit': 100},
 u'status': u'OPEN',
 u'submissionInstructionsMessage': u'In order to submit a Challenge Entry, your team will create a Synapse Project which will address the evaluation criteria for the Challenge, along with references to source code and a wiki documenting your methods.',
 u'submissionReceiptMessage': u'Congratulations! Your submission has been received and will be evaluated by the Challenge organizing committee.'}
    # {'status': u'OPEN', 'contentSource': u'syn5591679', 'submissionInstructionsMessage': u'To submit to the XYZ Challenge, send a tab-delimited file as described here: https://...', u'createdOn': u'2016-01-15T22:38:09.697Z', 'submissionReceiptMessage': u'Your submission has been received. For further information, consult the leader board at https://...', u'etag': u'a9e827f7-ca98-4157-bfb8-72bbb1617872', u'ownerId': u'3323072', u'id': u'5591680', 'name': u'Example Synapse Challenge d9372db4-986d-4870-8277-70c1dac57b0e'}
]
evaluation_queue_by_id = {q['id']:q for q in evaluation_queues}

## define the default set of columns that will make up the leaderboard
LEADERBOARD_COLUMNS = [
    dict(name='objectId',      display_name='ID',      columnType='STRING', maximumSize=20),
    dict(name='userId',        display_name='User',    columnType='STRING', maximumSize=20, renderer='userid'),
    dict(name='entityId',      display_name='Entity',  columnType='STRING', maximumSize=20, renderer='synapseid'),
    dict(name='versionNumber', display_name='Version', columnType='INTEGER'),
    dict(name='name',          display_name='Name',    columnType='STRING', maximumSize=240),
    dict(name='team',          display_name='Team',    columnType='STRING', maximumSize=240)]

## Here we're adding columns for the output of our scoring functions, score,
## rmse and auc to the basic leaderboard information. In general, different
## questions would typically have different scoring metrics.
leaderboard_columns = {}
for q in evaluation_queues:
    leaderboard_columns[q['id']] = LEADERBOARD_COLUMNS
    # + [
    #     dict(name='score',         display_name='Score',   columnType='DOUBLE'),
    #     dict(name='rmse',          display_name='RMSE',    columnType='DOUBLE'),
    #     dict(name='auc',           display_name='AUC',     columnType='DOUBLE')]

## map each evaluation queues to the synapse ID of a table object
## where the table holds a leaderboard for that question
leaderboard_tables = {}

## R command file to run archiving
R_ARCHIVE_COMMAND_PATH = '/home/ubuntu/Projects/U4CChallenge/R/archiveProject.R'

def validate_submission(evaluation, submission):
    """
    Find the right validation function and validate the submission.

    :returns: (True, message) if validated, (False, message) if
              validation fails or throws exception
    """

    messages = []

    # Validate access by evaluation panel
    v = validation_helpers.validate_panel_access(submission['entityId'], syn)

    if not v[0]:
        return v

    messages.append(v[1])

    try:
        w = syn.getWiki(submission['entityId'])
        wMarkdown = w['markdown']
    except synapseclient.client.SynapseHTTPError as e:
        v = (False, "Cannot read project - no permissions.")

    if not v[0]:
        return v

    # Validate header existence
    v = validation_helpers.validate_headers(wMarkdown)

    if not v[0]:
        return v

    messages.append(v[1])

    # Validate header order
    v = validation_helpers.validate_header_order(wMarkdown)

    if not v[0]:
        return v

    messages.append(v[1])

    # Validate word counts
    v = validation_helpers.validate_wordcounts(wMarkdown)

    if not v[0]:
        return v

    messages.append(v[1])
    # Validate non-empty abstract existence
    v = validation_helpers.validate_abstract(submission['entityId'], syn)

    if not v[0]:
        return v

    messages.append(v[1])

    final_message = "<br/>\n".join(messages)
    return (True, "<br/>\n%s\n<br/>\n" % (final_message, ))

def score_submission(evaluation, submission):
    """
    Find the right scoring function and score the submission

    :returns: (score, message) where score is a dict of stats and message
              is text for display to user
    """
    import random
    return (dict(score=random.random(), rmse=random.random(), auc=random.random()), "You did fine!")
