#!/usr/bin/env r

if (is.null(argv) | length(argv)<1) {
  cat("Usage: archiveProject.R submissionId\n")
  q()
}

library(synapseClient)
library(synapseCopyProject)

synapseLogin()

# Submission
submission <- synGetSubmission(argv[1])

# Old project
oldPId <- submission$entityId
oldP <- synGet(oldPId)

# Crawl it
G <- crawlSynapseObject(oldPId)

# New project will be copy of the old one
newP <- synStore(Project(name=paste("Archived ", as.numeric(Sys.time()), submission$id, oldP@properties$id, oldP@properties$name)))

# Perform a copy
pC <- copyProject(newP@properties$id, G, topId=newP@properties$id)

synSetAnnotations(newP) <- list(evaluationId=s$evaluationId, submissionId=submission$id,
                                submittingUserId=submission$userId, origEntityId=submission$entityId,
                                submittingTeamId=submission$teamId, projectName=oldP@properties$name)

newP <- synStore(newP)

# Create entity mapping to update wikis
entityMap <- pC$newid
names(entityMap) <- G$id

# copy Wikis
res <- lapply(seq_along(entityMap),
              function(i) tryCatch(copyWiki(names(entityMap[i]), entityMap[i],
                                            entityMap = entityMap),
                                   error=function(e) NULL))
