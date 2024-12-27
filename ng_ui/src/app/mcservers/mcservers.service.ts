import { Injectable } from '@angular/core';
import { HttpHeaders, HttpClient } from '@angular/common/http';
import { Observable, timer, of, forkJoin } from 'rxjs';
import { concatMap, tap, catchError, map, switchMap, mergeMap } from 'rxjs/operators';


import { AuthService } from '../auth/auth.service';
import { MCServer } from './models/mcserver';

const BASE_URL: string = '../api/servers';


@Injectable()
export class MCServersService {
    public servers!: Map<string, MCServer>;
    public servers$: Observable<MCServer[]>;

    constructor(
        private http: HttpClient,
        private auth: AuthService
    ) {
        // First get the initial servers list
        this.servers$ = this.getServers().pipe(
            // Switch to polling individual server details
            switchMap(initialServers => {
                // Create the polling observable for server details
                return timer(0, 10000).pipe(
                    // Map to current servers list
                    map(() => {
                        if (!this.servers) return [];
                        return Array.from(this.servers.values());
                    }),
                    tap(servers => {
                        // Start independent polling for each server
                        servers.forEach(server => {
                            this.getServerDetails(server).pipe(
                                tap(detailedServer => {
                                    const existingServer = this.servers.get(detailedServer.hostname);
                                    if (existingServer) {
                                        Object.assign(existingServer, detailedServer);
                                        this.updateLaunchPercentage(existingServer);
                                    }
                                }),
                                catchError(err => {
                                    console.log(`Error updating ${server.name}:`, err);
                                    return of(server);
                                })
                            ).subscribe();
                        });
                    }),
                )
            })
        );
    }

    private getServers(): Observable<MCServer[]> {
        console.log('Getting initial servers list');
        const url: string = `${BASE_URL}/`;
        const headers = this.getHeaders();
        
        return this.http.get<MCServer[]>(url, { headers }).pipe(
            map(servers => servers.reduce((map, obj) => {
                map.set(obj.hostname, obj);
                return map;
            }, new Map<string, MCServer>())),
            tap(servers => this.servers = servers),
            map(servers => Array.from(servers.values())),
            catchError(err => {
                console.log(err);
                return of(<MCServer[]>[]);
            })
        );
    }

    private updateLaunchPercentage(server: MCServer): void {
		if (server.online || !server.launching) {
			server.launch_pct = undefined;
			return;
		}
        if (server.launch_time !== undefined && server.launching === true) {
            console.log(`Calculating launch_pct for ${server.name}`);
            const timeoutMins = 15;
            const launchTime = new Date(server.launch_time * 1000);
            const currentTime = new Date();
            const minutesAgo = (currentTime.getTime() - launchTime.getTime()) / (1000 * 60);
            
            if (minutesAgo < timeoutMins) {
                const launchPct = (minutesAgo / timeoutMins) * 100;
                server.launch_pct = launchPct;
            } else {
                server.launch_pct = undefined;
            }
        } else {
            server.launch_pct = undefined;
        }
    }

	getServerDetails(server: MCServer): Observable<MCServer> {
		console.log(`Checking server: ${server.name}`);
		const url: string = `${BASE_URL}/${server.hostname}`;
		const headers = this.getHeaders();
		return this.http.get<MCServer>(url, { headers: headers }).pipe(
			catchError(err => {
				console.log(err);
				return of({...server});
			})
		);
	}

	public launch(server: MCServer) {
		console.log('Launching server');
		const url: string = `${BASE_URL}/${server.hostname}/launch`;
		const headers = this.getHeaders();
		server.launch_pct = 0.1;
		this.http.put<MCServer>(url, null, { headers: headers }).pipe(
			tap(_ => {
				this.getServers().subscribe();
			}),
			catchError(err => {
				console.log(err);
				return new Observable();
			})
		).subscribe();
	}

	getHeaders() {
		return new HttpHeaders({
			'Content-Type': 'application/json',
			'Authorization': `Bearer ${this.auth.getIdToken()}`
		});
	}
}

/*
@Injectable()
export class MCServersService {
	public servers!: Map<string, MCServer>;
	public servers$: Observable<MCServer[]>;

	constructor(
		private http: HttpClient,
		private auth: AuthService
	) {
		this.servers$ = timer(0, 5000).pipe(
			concatMap(_ => this.getServers())
		);
	}

	getServers(): Observable<MCServer[]> {
		console.log('Checking servers');
		const url: string = `${BASE_URL}/`;
		const headers = this.getHeaders();
		return this.http.get<MCServer[]>(url, { headers: headers }).pipe(
			map(servers => servers.reduce((map, obj) => {
				map.set(obj.hostname, obj);
				return map;
			}, new Map())),
			tap(servers => {
				servers.forEach((server, hostName) => {
					if (this.servers) {
						const prevServer = this.servers.get(server.hostname);
						if (prevServer) {
							Object.assign(server, prevServer);
						}
					}
				});
			}),
			tap(servers => this.servers = servers),
			tap(servers => {
				servers.forEach((server: MCServer, hostName: string) => {
					this.getServerDetails(server).pipe(
						tap(detailedServer => {
							console.log('Detailed server from service:', detailedServer)
							Object.assign(server, detailedServer);
							// Calculate launch_pct if launch time is less than 15 minutes ago and it's still offline
							if (server.launch_time !== undefined && server.launching === true) {
								console.log(`Calculating launch_pct for ${server.name}`);
								const timeoutMins = 15;
								const launchTime = new Date(server.launch_time * 1000);
								const currentTime = new Date();
								const minutesAgo = (currentTime.getTime() - launchTime.getTime()) / (1000 * 60);
								console.log('Minutes ago:', minutesAgo);
								if (minutesAgo < timeoutMins) {
									const launchPct = (minutesAgo / timeoutMins) * 100;
									console.log('Setting launch_pct:', launchPct);
									server.launch_pct = launchPct;
								} else {
									console.log('Unsetting launch_pct');
									server.launch_pct = undefined;
								}
							} else {
								console.log('Unsetting launch_pct');
								server.launch_pct = undefined;
							}
						})
					).subscribe();
				});
			}),
			map(servers => {
				return Array.from(servers.values())
			}),
			catchError(err => {
				console.log(err);
				return of(<MCServer[]>{});
			})
		);
	}


}
*/