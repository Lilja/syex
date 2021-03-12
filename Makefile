run-local:
	docker build -t dev/syex . && docker run -p 19999:9999 --env-file ../../homelab/secrets/synology.env --rm dev/syex
