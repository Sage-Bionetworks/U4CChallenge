##-----------------------------------------------------------------------------
##
## challenge specific code and configuration
##
##-----------------------------------------------------------------------------

import validation_helpers
import synapseclient
syn = synapseclient.login()

## A Synapse project will hold the assetts for your challenge. Put its
## synapse ID here, for example
## CHALLENGE_SYN_ID = "syn1234567"
CHALLENGE_SYN_ID = "syn5591679"

## Name of your challenge, defaults to the name of the challenge's project
CHALLENGE_NAME = "Example Synapse Challenge"

## Synapse user IDs of the challenge admins who will be notified by email
## about errors in the scoring script
ADMIN_USER_IDS = ["3323072"]

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
    {'status': u'OPEN', 'contentSource': u'syn5591679', 'submissionInstructionsMessage': u'To submit to the XYZ Challenge, send a tab-delimited file as described here: https://...', u'createdOn': u'2016-01-15T22:38:09.697Z', 'submissionReceiptMessage': u'Your submission has been received. For further information, consult the leader board at https://...', u'etag': u'a9e827f7-ca98-4157-bfb8-72bbb1617872', u'ownerId': u'3323072', u'id': u'5591680', 'name': u'Example Synapse Challenge d9372db4-986d-4870-8277-70c1dac57b0e'}]
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
    leaderboard_columns[q['id']] = LEADERBOARD_COLUMNS + [
        dict(name='score',         display_name='Score',   columnType='DOUBLE'),
        dict(name='rmse',          display_name='RMSE',    columnType='DOUBLE'),
        dict(name='auc',           display_name='AUC',     columnType='DOUBLE')]

## map each evaluation queues to the synapse ID of a table object
## where the table holds a leaderboard for that question
leaderboard_tables = {}


def validate_submission(evaluation, submission):
    """
    Find the right validation function and validate the submission.

    :returns: (True, message) if validated, (False, message) if
              validation fails or throws exception
    """

    w = syn.getWiki(submission['entityId'])
    wMarkdown = w['markdown']

    # Validate header existence
    v = validation_helpers.validate_headers(wMarkdown)

    if not v[0]:
        return v

    # # Validate header order
    # v = validation_helpers.validate_header_order(wMarkdown)

    # if not v[0]:
        # return v

    # Validate word counts
    v = validation_helpers.validate_wordcounts(wMarkdown)

    if not v[0]:
        return v

    return True, "A-OK."

def score_submission(evaluation, submission):
    """
    Find the right scoring function and score the submission

    :returns: (score, message) where score is a dict of stats and message
              is text for display to user
    """
    import random
    return (dict(score=random.random(), rmse=random.random(), auc=random.random()), "You did fine!")