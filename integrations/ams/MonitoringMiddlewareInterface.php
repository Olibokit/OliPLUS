<?php

namespace Aws\ClientSideMonitoring;

use Aws\CommandInterface;
use Aws\Exception\AwsException;
use Aws\ResultInterface;
use Psr\Http\Message\RequestInterface;

/**
 * Interface for client-side monitoring middleware.
 *
 * @internal
 */
interface MonitoringMiddlewareInterface
{
    /**
     * Extracts request data for monitoring.
     *
     * @param RequestInterface $request
     * @return array<string, mixed>
     */
    public static function getRequestData(RequestInterface $request): array;

    /**
     * Extracts response or error data for monitoring.
     *
     * @param ResultInterface|AwsException|\Exception $response
     * @return array<string, mixed>
     */
    public static function getResponseData($response): array;

    /**
     * Middleware handler invoked during command execution.
     *
     * @param CommandInterface $cmd
     * @param RequestInterface $request
     * @return callable
     */
    public function __invoke(CommandInterface $cmd, RequestInterface $request);
}
