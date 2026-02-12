from django.utils.text import slugify


class SlugifyMixin:
    slug_field = "slug"       # champ qui reçoit le slug
    source_field = "name"  
    # champ source utilisé pour générer le slug

    def save(self, *args, **kwargs):
        source_value = getattr(self, self.source_field, None)
        if source_value:
            base_slug = slugify(source_value)
            slug = base_slug
            counter = 1

            # Vérifie si le slug existe déjà (hors instance courante en update)
            Model = self.__class__
            while Model.objects.filter(**{self.slug_field: slug}).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            setattr(self, self.slug_field, slug)

        return super().save(*args, **kwargs)
