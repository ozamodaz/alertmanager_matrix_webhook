# alertmanager_matrix_webhook
Helper to post alerts from Prometheus Alertmanager to Matrix (https://matrix.org/) room.

Usage
1. Register Account you will use as Bot
2. Get access_token like this:
```
curl -XPOST -H "Content-Type: application/json" -d '{
  "type": "m.login.password",
  "user": "your_username",
  "password": "your_password"
}' https://your.matrix.server/_matrix/client/r0/login
```
The response will be a JSON object that includes your access_token, user_id, and other details. For example:
```
{
  "user_id": "@your_username:your.matrix.server",
  "access_token": "s3cr3t_T0k3n_here",
  "device_id": "ABC123XYZ",
  "well_known": { ... }
}
```
3. Get Room id. Element: Room Settings -> Advanced -> Internal room ID
4. Fill all Env values to docker-compose.yaml
3. Run docker-compose and use example prometheus-alertmanager configs
