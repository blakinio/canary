<?php

declare(strict_types=1);

use App\Accounts\Models\IdentityCanaryAccount;
use App\GameAuth\OAuth\NativeOAuthClientManager;
use App\GameAuth\Worlds\GameWorld;
use App\GameAuth\Worlds\GameWorldStatus;
use App\Identity\Models\Identity;
use Illuminate\Contracts\Console\Kernel;
use Illuminate\Support\Facades\Hash;

require '/app/vendor/autoload.php';
$app = require '/app/bootstrap/app.php';
$app->make(Kernel::class)->bootstrap();

$email = getenv('REHEARSAL_IDENTITY_EMAIL') ?: '';
$password = getenv('REHEARSAL_IDENTITY_PASSWORD') ?: '';
$accountId = (int) (getenv('REHEARSAL_CANARY_ACCOUNT_ID') ?: '0');
$worldHost = getenv('REHEARSAL_WORLD_HOST') ?: '';
$worldPort = (int) (getenv('REHEARSAL_WORLD_PORT') ?: '0');
$output = getenv('REHEARSAL_BOOTSTRAP_OUTPUT') ?: '/evidence/platform-bootstrap.json';

if ($email === '' || $password === '' || $accountId < 1 || $worldHost === '' || $worldPort < 1 || $worldPort > 65535) {
    throw new RuntimeException('Incomplete rehearsal bootstrap environment.');
}

$identity = Identity::query()->updateOrCreate(
    ['email' => $email],
    ['password' => Hash::make($password)],
);

IdentityCanaryAccount::query()->updateOrCreate(
    ['identity_id' => $identity->id],
    [
        'canary_account_id' => $accountId,
        'provisioning_name' => 'ephemeral_rehearsal_'.$identity->id,
        'canary_creation_epoch' => 1,
        'status' => IdentityCanaryAccount::STATUS_READY,
        'last_failure_code' => null,
        'ready_at' => now(),
    ],
);

$world = GameWorld::query()->updateOrCreate(
    ['slug' => 'canary-e2e'],
    [
        'name' => 'Canary E2E',
        'region' => 'ephemeral',
        'status' => GameWorldStatus::Online,
        'login_enabled' => true,
        'game_host' => $worldHost,
        'game_port' => $worldPort,
    ],
);

/** @var NativeOAuthClientManager $clients */
$clients = $app->make(NativeOAuthClientManager::class);
$client = $clients->ensure();

$payload = [
    'schema_version' => 1,
    'identity_id' => (int) $identity->id,
    'canary_account_id' => $accountId,
    'world_id' => (int) $world->id,
    'oauth_client_id' => (string) $client->getKey(),
    'oauth_client_confidential' => $client->confidential(),
    'oauth_client_has_secret' => $client->getAttribute('secret') !== null,
    'oauth_client_redirect_uris' => $client->getAttribute('redirect_uris'),
];

file_put_contents($output, json_encode($payload, JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES)."\n");
