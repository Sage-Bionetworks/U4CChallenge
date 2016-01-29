def main():
  import validation_helpers
  import synapseclient

  syn = synapseclient.Synapse()
  syn.login()

  assert syn.getPermissions('syn4154450', 3331171) == [u'READ']
  
  # w = syn.getWiki("syn4154450")
  #
  # wMarkdown = w['markdown']
  #
  # print validation_helpers.validate_header_order(wMarkdown)
  # print validation_helpers.validate_wordcounts(wMarkdown)

if __name__ == "__main__":
  main()
