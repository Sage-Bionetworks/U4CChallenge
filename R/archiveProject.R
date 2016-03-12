#!/usr/bin/env r

# Currently requires
devtools::install_github("Sage-Bionetworks/rSynapseUtilities", ref="updatecopywiki")

if (is.null(argv) | length(argv)<1) {
  cat("Usage: archiveProject.R submissionId\n")
  q()
}

library(synapseClient)
# library(synapseUtilities)
library(rSynapseUtilities)

synapseLogin()

# Submission
submission <- synGetSubmission(argv[1])

# Old project
oldPId <- submission$entityId
oldP <- synGet(oldPId)

# Crawl it
G <- crawlSynapseObject(oldPId)

# New project will be copy of the old one
newP <- Project(name=paste("Archived ", as.numeric(Sys.time()), submission$id, oldP@properties$id, oldP@properties$name))

synSetAnnotations(newP) <- list(evaluationId=submission$evaluationId, submissionId=submission$id,
                                submittingUserId=submission$userId, origEntityId=submission$entityId,
                                submittingTeamId=submission$teamId, projectName=oldP@properties$name,
                                archived=FALSE)

newP <- synStore(newP)

# Perform a copy
pC <- copyProject(newP@properties$id, G, topId=newP@properties$id)

synSetAnnotation(newP, "archived") <- TRUE

newP <- synStore(newP)

# Create entity mapping to update wikis
entityMap <- pC$newid
names(entityMap) <- G$id

# copy Wikis
res <- lapply(seq_along(entityMap),
              function(i) tryCatch(copyWiki(names(entityMap[i]),
                                            entityMap[i],
                                            updateLinks=FALSE, 
                                            updateSynIds=FALSE),
                                   # entityMap=entityMap),
                                   error=function(e) NULL))
