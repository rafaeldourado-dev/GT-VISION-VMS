import { Home, Map, Camera, FileText, Settings } from 'lucide-react';

export default function Sidebar() {
  return (
    <aside className="fixed inset-y-0 left-0 z-10 hidden w-14 flex-col border-r bg-background sm:flex">
      <nav className="flex flex-col items-center gap-4 px-2 sm:py-5">
        <a href="#" className="group flex h-9 w-9 shrink-0 items-center justify-center gap-2 rounded-full bg-primary text-lg font-semibold text-primary-foreground md:h-8 md:w-8 md:text-base">
          {/* Você pode colocar sua Logo aqui */}
          <span className="sr-only">GT-Vision</span>
        </a>
        <a href="#" className="flex h-9 w-9 items-center justify-center rounded-lg text-muted-foreground transition-colors hover:text-foreground md:h-8 md:w-8">
          <Home className="h-5 w-5" />
          <span className="sr-only">Dashboard</span>
        </a>
        <a href="#" className="flex h-9 w-9 items-center justify-center rounded-lg bg-accent text-accent-foreground transition-colors hover:text-foreground md:h-8 md:w-8">
          <Map className="h-5 w-5" />
          <span className="sr-only">Mapa ao Vivo</span>
        </a>
        <a href="#" className="flex h-9 w-9 items-center justify-center rounded-lg text-muted-foreground transition-colors hover:text-foreground md:h-8 md:w-8">
          <Camera className="h-5 w-5" />
          <span className="sr-only">Câmeras</span>
        </a>
        <a href="#" className="flex h-9 w-9 items-center justify-center rounded-lg text-muted-foreground transition-colors hover:text-foreground md:h-8 md:w-8">
          <FileText className="h-5 w-5" />
          <span className="sr-only">Relatórios</span>
        </a>
      </nav>
      <nav className="mt-auto flex flex-col items-center gap-4 px-2 sm:py-5">
        <a href="#" className="flex h-9 w-9 items-center justify-center rounded-lg text-muted-foreground transition-colors hover:text-foreground md:h-8 md:w-8">
          <Settings className="h-5 w-5" />
          <span className="sr-only">Configurações</span>
        </a>
      </nav>
    </aside>
  );
}