
# vault-secrets-downloader

A tool that grabs secrets key: value data from hachicorp vault and saves it with formatting.




## Usage/Examples
Put the executable wherever you want, check you have permission to run it and it has +x flag.
Create config.yml and put it to one of these directories:
 - directory containing the executable
 - `/etc/hachivsd`
 - `~/.config/hachivsd`
then run the executable
```bash
hachivsd
```
## Config

```yaml
---
vault:
  url: "http://your.vault.addr"
  token: read-only-token-for-engine
  engine: k-v-engine-name
output: 
  basepath: ./path
  path-override: out/
  mode-override: none
  name-prefix: envos
  name-suffix: .env
```
All of **Vault** section parameters are mandatory,
and the **output basepath** too.
Other parameters are optional and will override the `__type__`, `__filename__` and `__path__` parameters in secret.
