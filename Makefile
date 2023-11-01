PATH := ~/.solc-select/artifacts/solc-0.8.16:~/.solc-select/artifacts:$(PATH)
certora-chief :; PATH=${PATH} certoraRun certora/DssChief.conf$(if $(rule), --rule $(rule),)
