import { createContext, useContext, useRef, type ReactNode } from "react";
import { RuntimeKernel } from "../core/runtime/kernel/RuntimeKernel";
import { StateModule } from "../core/runtime/modules/StateModule";
import { SessionModule } from "../core/runtime/modules/SessionModule";
import { EventRecorder } from "../core/runtime/modules/EventRecorder";

const RuntimeContext = createContext<RuntimeKernel | null>(null);

export function RuntimeProvider({ children }: { children: ReactNode }) {
  const kernelRef = useRef<RuntimeKernel | null>(null);

  if (!kernelRef.current) {
    const kernel = new RuntimeKernel({});
    kernel.context.registry.register(new StateModule());
    kernel.context.registry.register(new SessionModule());
    kernel.context.registry.register(new EventRecorder());
    kernelRef.current = kernel;
  }

  return (
    <RuntimeContext.Provider value={kernelRef.current}>
      {children}
    </RuntimeContext.Provider>
  );
}

export function useRuntime() {
  const kernel = useContext(RuntimeContext);
  if (!kernel) {
    throw new Error("useRuntime must be used within RuntimeProvider");
  }
  return kernel;
}
