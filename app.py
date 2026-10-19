        repo_path.resolve()
    )
    
    console.print("[bold cyan]Low Bus Factor (knowledge silos)[/bold cyan]")
    calculate_bus_factor(repo_path)

    console.print("[green]✅ Running code metrics on your project...[/green]\n")
    console.print("[cyan]These include complexsity, coupling, bugs hotspots, and more...[/cyan]")
    print(colored("  Run `nxdo metrics --help` for details.", "cyan"))
    _print_auto_health_report(repo_path)
    _generate_and_sync_auto_tickets(repo_path, extra_context)
    _print_auto_health_report(repo_path)

    return 0
