PATH := ~/.solc-select/artifacts/solc-0.8.16:~/.solc-select/artifacts:$(PATH)
certora-chief            :; PATH=${PATH} certoraRun certora/DssChief.conf --exclude_rule entryPoints storageAffected$(if $(rule), --rule $(rule),)$(if $(results), --wait_for_results all,)
certora-chief-parametric :; PATH=${PATH} certoraRun certora/DssChief.conf --rule entryPoints storageAffected --optimistic_loop$(if $(results), --wait_for_results all,)
