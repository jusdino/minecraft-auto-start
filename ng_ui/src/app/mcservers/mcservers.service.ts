import { Injectable } from '@angular/core';
import { HttpHeaders, HttpClient } from '@angular/common/http';
import { Observable, timer, of } from 'rxjs';
import { concatMap, tap, catchError, map } from 'rxjs/operators';

import { AuthService } from '../auth/auth.service';
import { MCServer } from './models/mcserver';

const BASE_URL: string = '../api/servers';


@Injectable({
	providedIn: 'root'
})
export class MCServersService {
	public servers: Map<string, MCServer>;
	public newServer: MCServer = new MCServer();
	public servers$: Observable<MCServer[]>;

	constructor(
		private http: HttpClient,
		private auth: AuthService
	) {
		this.servers$ = timer(0, 5000).pipe(
			concatMap( _ => this.getServers())
		);
	}

	getServers(): Observable<MCServer[]> {
		console.log('Checking servers');
		const url: string = `${BASE_URL}/`;
		const headers = this.getHeaders();
		return this.http.get<MCServer[]>(url, {headers: headers}).pipe(
			map( servers => servers.reduce((map, obj) => {
				map.set(obj.hostname, obj);
				return map;
			}, new Map())),
			tap(servers => {
				servers.forEach((server, hostName) => {
					if (this.servers) {
						const prev_server = this.servers.get(server.hostname);
						if (prev_server) {
							server.hostname = prev_server.hostname;
							if (prev_server.launch_time) {
								server.launch_time = prev_server.launch_time;
								server.launch_pct = prev_server.launch_pct;
							} else {
								server.launch_pct = null;
							}
							server.name = prev_server.name;
							server.status = prev_server.status;
							server.status_time = prev_server.status_time;
							server.version = prev_server.version;
						}
					}
				});
			}),
			tap(servers => this.servers = servers),
			tap(servers  => {
				servers.forEach((server, hostName) => {
 					this.getServerDetails(server).pipe(
						tap(detailedServer => {
							server.hostname = detailedServer.hostname;
							// Cast to number
							if (detailedServer.launch_time) {
								server.launch_time = +detailedServer.launch_time;
								// Percent of a 10 minute timeout elapsed since launch_time
								server.launch_pct = (Date.now()/1000 - server.launch_time)/6;
							} else {
								server.launch_pct = null;
							}
							server.name = detailedServer.name;
							server.status = detailedServer.status;
							if (detailedServer.status_time) {
								server.status_time = +detailedServer.status_time;
							}
							server.version = detailedServer.version;
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

	getServerDetails(server: MCServer): Observable<MCServer> {
		console.log(`Checking server: ${server.name}`);
		const url: string = BASE_URL + '/' + server.hostname;
		const headers = this.getHeaders();
		return this.http.get<MCServer>(url, {headers: headers}).pipe(
			catchError(err => {
				console.log(err);
				return of();
			})
		);
	}

	public submitNew() {
		console.log('Submitting new server');
		const url: string = `${BASE_URL}/`;
		const headers = this.getHeaders();
		this.http.post<MCServer>(url, this.newServer, {headers: headers}).pipe(
			tap( server => {
				this.newServer = new MCServer();
				this.getServers().subscribe();
			}),
			catchError(err => {
				console.log(err);
				return null;
			})
		).subscribe();
	}

	public launch(server: MCServer) {
		console.log('Launching server');
		const url: string = `${BASE_URL}/${server.hostname}`;
		const headers = this.getHeaders();
		server.launch_pct = 0.1;
		this.http.put<MCServer>(url, null, {headers: headers}).pipe(
			tap( server => {
				this.getServers().subscribe();
			}),
			catchError(err => {
				console.log(err);
				return null;
			})
		).subscribe();
	}

	getHeaders() {
		return new HttpHeaders({
			'Content-Type': 'application/json',
			'Authorization': `Bearer ${this.auth.authContext.session.getIdToken().getJwtToken()}`
		});
	}
}
