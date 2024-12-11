---
layout: single
title: Progressive Forms with React 19
date: 2024-12-11
---
So, React 19 is here! And Server Components and Forms are now the blessed way. It's like old-school backend-first web-dev all over again but with two great advantages:
1. Full-stack type-safety
2. You can inject client-side interactivity when needed

_In the beginning_, the only way with React was single-page-apps (SPAs) with mountains of clunky state and AJAX. Things improved and Routers were invented, and [useQuery](https://tanstack.com/query/latest/docs/framework/react/reference/useQuery) made data fetching and management easier. But state is _hard_! Every read or mutation has several layers where state can persist, and subtle interdependencies. Not to mention there's no graceful downgrade if JavaScript isn't available, and you have to ship loads of the stuff to make it all work on the client.

[Remix](https://remix.run/) pushed hard on forms and backend routing. Hit a form, reload. Next.js saw that this was good, so they created the App router and a nightmare transition for their users, but the dust is now settling (at least for greenfield projects). And now all this stuff has found its way into React itself, in the form [React Server Components](https://react.dev/reference/rsc/server-components) and new Form tooling.

But they're new and slightly weird and the best patterns for some basic things still aren't obvious. Specifically:
1. Data validation
2. Handling errors
3. Maintaining state
4. Optimistic loading

So I played around a bit and came up with what I think is a pretty good setup for fancy React 19 forms. I'm going to assume you're already familiar with with Server Components and `"use server"` and forms in general. If not, it's worth reading [the Next.js docs on the topic](https://nextjs.org/docs/app/building-your-application/data-fetching/server-actions-and-mutations) and following the interesting links where they lead. As always, you can just skip to the repo [carderne/react-forms](https://github.com/carderne/react-forms) (or scroll to the bottom) if you prefer.

## Starting point
A basic server action with some [zod](https://zod.dev/) validation. You can also use [zod-form-data](https://www.npmjs.com/package/zod-form-data) to make some of this more ergonomic.
```ts
// actions.ts
"use server";
import { redirect } from "next/navigation";
import { z } from "zod";

const schema = z.object({
  todo: z.string().min(3, { message: "Please write more!" }),
});

export async function addItemAction(
  formData: FormData
) {
  const obj = Object.fromEntries(formData);
  const data = schema.parse(obj);
  console.log(data); // or, you know, persist to DB
  redirect("/");
}
```

And a form to use it.
```tsx
// form.tsx
import Form from "next/form";
import { addItemAction } from "./actions";

export function ItemForm() {
  return (
    <Form action={addItemAction}>
      <input name="todo" />
      <button type="submit">
        Submit
      </button>
    </Form>
  )
}
```

That works pretty well. And it's so simple compared to "modern" ways of mutating data. You persist the data, redirect as needed, and wherever the user lands will load the data. This means all the complex state stuff stays in the database, where it belongs.
## Error handling
The only problem with the code above is that it does nothing for errors. For example, the `todo` field requires a minimum of 3 characters. If the user enters only two, it will throw and the user will get an error page.

So of course you use `schema.safeParse(...)` but then what do you do with the error? This is where React 19 comes in, with the new [useActionState](https://react.dev/reference/react/useActionState) hook. It wraps your action and gives you a `state` object where your server code can return errors and messages for the client.

On the backend, we return an object with an `errors` field (you're obviously free to call this whatever you want). And we can use some handy `zod` methods to create error messages keyed to the schema fields.
```ts
// actions.ts
"use server";
import { redirect } from "next/navigation";
import { z } from "zod";

const schema = z.object({
  todo: z.string().min(3, { message: "Please write more!" }),
});

export interface AddItemState {//+
  errors: { todo: string[] }//+
}//+

export async function addItemAction(
  _state: AddItemState,//+
  formData: FormData
): Promise<AddItemState> {//+
  const obj = Object.fromEntries(formData);
  const { data, error } = schema.safeParse(obj);
  if (error) {//+
    return {//+
      errors: error.flatten().fieldErrors//+
    }//+
  }//+
  console.log(data);
  redirect("/");
}
```

And the form. When there's a validation error from entering a too-short string, it'll display the "Please write more!" message above the input. We also get a nice Loading state with the `pending` value from the hook.
```tsx
// form.tsx
"use client"; // this must be client side now//+

import Form from "next/form";
import { useActionState } from "react";//+
import { addItemAction, type AddItemState } from "./actions";//+

export function ItemForm() {
  const [state, formAction, pending] = useActionState<AddItemState, FormData>(//+
    addItemAction,  // our action//+
    {},             // and default state//+
  );//+
  return (
    <Form action={formAction}>//+
      <div>{state.errors?.todo?.map((e) => e)}</div>//+
      <input name="todo" />
      <button type="submit">
        {pending ? "Loading" : "Submit"}//+
      </button>
    </Form>
  );
}
```

## Maintaining client state
That's a big improvement but there's still one problem: every time you hit a validation error, the form will reset. This is to maintain parity with native forms, which reset as soon as they're submitted. There's a massive thread at [facebook/react#29034](https://github.com/facebook/react/issues/29034) discussing this{%- include fn.html n=1 -%}, with two main approaches shared for getting around this:

1. Submit the form manually using `onSubmit`
2. Return all the original form data as part of the `AddItemState` return value.

I'm going to show the second option, mostly because it lets us get further without resorting to imperative logic, and it seems a bit more elegant. But with very complex (multi-step) forms, some combination of the two could be required.

Here's our code again. I added some type helpers that you can re-use wherever you have a form. These take any `zod` schema and create a neat return type with the `FormData` plus an array of error messages for each field in the schema.
```ts
// types.ts
type InferFieldErrors<T extends z.ZodType> = {
  [K in keyof z.infer<T>]?: string[] | undefined;
};
export type ActionState<T extends z.ZodType> = {
  formData?: FormData;
  errors?: InferFieldErrors<T>;
};
```

And here's the action. The key differences being the fact that we now return `formData` in the error path (and the new `AddItemState` created using the helpers above).
```ts
// actions.ts
"use server";
import { redirect } from "next/navigation";
import { z } from "zod";
import { type ActionState } from "./types";//+

const addItemSchema = z.object({
  todo: z.string().min(3, { message: "Text must be longer" }),
});
export type AddItemState = ActionState<typeof addItemSchema>;//+

export async function addItemAction(
  _state: AddItemState,
  formData: FormData,
): Promise<AddItemState> {
  const formDataObj = Object.fromEntries(formData);
  const { data, error } = addItemSchema.safeParse(formDataObj);
  if (error) {
    return {
      formData, // we return the formData as-is//+
      errors: error.flatten().fieldErrors,
    };
  }
  console.log(data);
  redirect("/");
}
```

And the form. The type cast on the `defaultValue` isn't wonderful, and there are cases with `<select>` (not to mention file uploads) that will need more careful consideration (and probably just being controlled components client side).
```tsx
// form.tsx
"use client";

import Form from "next/form";
import { useActionState } from "react";
import { addItemAction, type AddItemState } from "./actions";

// imagine we have some `item` being passed to the component
export function ItemForm({ item }: { item: string }) {//+
  const [state, formAction, pending] = useActionState<AddItemState, FormData>(
    addItemAction,
    {},
  );
  return (
    <Form action={formAction}>
      <div>{state.errors?.todo?.map((e) => e)}</div>
      <input
        name="todo"
        // and we show the formData if we have it, otherwise `item`//+
        defaultValue={(state.formData?.get("todo") as string) ?? item}//+
      />
      <button type="submit">
        {pending ? "Loading" : "Submit"}
      </button>
    </Form>
  );
}

```

Now when the action returns an error, it will _also_ return the data we sent it. It's a bit silly flinging data back-and-forth like that, but so long as it's relatively small it should be fine. Also the returned `formData` doesn't need to be re-serialised, so that's nice.

## Optimism
Some Forms redirect somewhere (e.g. create a new thing, then redirect to it). But many are adding stuff to some form of table or list, and you just want to see your new item added to that. In client-side React, you'd typically have some `useState` and then push items into an array. Or with Tanstack, have a `useMutation` that invalidates a `useQuery` cache.

And with our approach, instead of redirecting as we've been doing, we'll rather `revalidate` the path (in Next.js-speak). We'd also like to add an optimistic update to the Form: as soon as you hit submit, optimistically add the item to the table/list, then forward it to the backend action, and then reload the component with the new data. Note that this can force you down the path of validating your inputs on the frontend (as well as the backend), because otherwise you'll see things appearing and then disappearing if there's a validation error on the backend.

The way we do this is with React 19's new [useOptimistic](https://react.dev/reference/react/useOptimistic) hook. If you try to use it with a Server Component-heavy approach, you'll immediately notice a problem: because `useOptimistic` is about sharing state between your Form and your Table, you'll have to bring it higher in the component tree _and_ force the containing component to be rendered client side. Not ideal. But fortunately there's an elegant solution: `Context`. I'm not going to show _all_ the code, but following [this handy blog post](https://aurorascharff.no/posts/utilizing-useoptimistic-across-the-component-tree-in-nextjs), we can do some clever stuff.

Firstly, some pretty standard context code. This is almost 100% boilerplate, so you can use the same pattern in various places.
```tsx
// optimistic.tsx
"use client";

import { createContext, useContext, useOptimistic } from "react";
import { Item } from "./types";

// The type here will need to include everything you show in the
// table, which may be a superset/subset of the zod schema
type Item = { ... }

type ContextType = {
  optimistic: Item[];
  addOptimistic: (_: Item) => void;
};

const Context = createContext<ContextType | undefined>(undefined);

export function OptimisticProvider({
  children,
  items,
}: {
  children: React.ReactNode;
  items: Item[];
}) {
  const [optimistic, addOptimistic] = useOptimistic(
    items,
    (state: Item[], newItem: Item) => {
      return [...state, newItem];
    }
  );

  return <Context value={{ optimistic, addOptimistic }}>{children}</Context>;
}

export function useOptimisticContext() {
  return useContext(Context);
}
```

Then in our containing page, which can remain a server component.
```tsx
// page.tsx
import { OptimisticProvider } from "./optimistic";
import { ItemForm } from "./form";
import { ItemTable } from "./table"; // we'll see this shortly
import { getItems } from "./db"; // pretend this exists

export default function Home() {
  const items = getItems();
  return (
    <OptimisticProvider items={items}>
      <ItemForm />
      <ItemTable />
    </OptimisticProvider>
  );
}
```

Now our Form component is quite different. If you want to pull out the Submit menu into a separate component (quite likely), you can use the other new [useFormStatus](https://react.dev/reference/react-dom/hooks/useFormStatus) hook to access the containing form's `pending` state without having to pass props around. Note that the backend action is unchanged for this round (phew!).
```tsx
// form.tsx
"use client";

import Form from "next/form";
import { useActionState, useRef } from "react";//+
import { useOptimisticContext } from "./optimistic";//+
import { addItemAction, type AddItemState } from "./actions";

export function ItemForm() {
  const ref = useRef<HTMLFormElement>(null);//+
  const { addOptimistic } = useOptimisticContext();//+
  const [state, formAction, pending] = useActionState<AddItemState, FormData>(
    addItemAction,
    {},
  );
  const optimisticAction = (formData: FormData) => {//+
    addOptimistic({//+
      todo: formData.get("todo") as string,//+
    });//+
    ref.current?.reset();//+
    formAction(formData);//+
  };
  return (
    <Form ref={ref} action={optimisticAction}>//+
      <div>{state.errors?.todo?.map((e) => e)}</div>
      <input
        name="todo"
        defaultValue={(state.formData?.get("todo") as string) ?? ""}
      />
      <button type="submit">
        {pending ? "Loading" : "Submit"}
      </button>
    </Form>
  );
}
```

And finally we can use our optimistically-updated data in some kind of table or list component:
```tsx
// table.tsx
"use client";

import { useOptimisticContext } from "./optimistic";

export function ItemTable() {
  const { optimistic } = useOptimisticContext();
  return (
    <div>
      {optimistic.map((item, idx) => (
        <div key={idx}>{item.todo}</div>
      ))}
    </div>
  );
}

```

And that's it. You now have a fully-featured form that degrades gracefully in the absence of JavaScript, handles validation and errors with aplomb, and gives nice snappy SPA-esque optimistic loading of entered data.

You can find the full code at [carderne/react-forms](https://github.com/carderne/react-forms). I think the `ActionState` types and approach are relatively elegant, but I'm curious to see what other patterns emerge. I'm really enjoying Server Components: it seems like after all the misadventures of needless SPAs and Redux, there's a happy path for lightly stateful multi-page apps, that can gracefully upgrade and downgrade as required.

And hopefully the fact that it's been upstreamed into React will make it easier for Remix (slash React Router) and other to continue to offer compelling alternatives to Next.js, who are worrying dominant.

Yes yes, [Astro](https://astro.build/) is a thing too.

------------------------------

{% include fnn.html n=1 note="Enjoyed seeing some Next.js docs writers chiming in that they were also scratching their heads a bit." %}

<script src="/assets/diff.js"></script>