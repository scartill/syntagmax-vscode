import * as path from 'path';
import { workspace, ExtensionContext } from 'vscode';
import { LanguageClient, LanguageClientOptions, ServerOptions } from 'vscode-languageclient/node';

let client: LanguageClient;

export function activate(context: ExtensionContext) {
    const serverModule = context.asAbsolutePath(path.join('server', 'server.py'));
    
    // Use python from path
    const serverOptions: ServerOptions = {
        command: 'python',
        args: [serverModule],
    };

    const clientOptions: LanguageClientOptions = {
        documentSelector: [{ scheme: 'file', language: 'syntagmax' }],
        synchronize: {
            fileEvents: workspace.createFileSystemWatcher('**/.stmx')
        }
    };

    client = new LanguageClient(
        'syntagmaxLanguageServer',
        'Syntagmax Language Server',
        serverOptions,
        clientOptions
    );

    client.start();
}

export function deactivate(): Thenable<void> | undefined {
    if (!client) {
        return undefined;
    }
    return client.stop();
}
