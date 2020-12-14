from django.db import models

class DPBaseManager(models.Manager):
    # A child class must implement:
    #
    # --> matchattr #### default 'name'
    # --> update_fields_to_exclude #### default ['id']
    # --> is_bulk_create #### default False
    #
    # --> get_parentqueryset(self, parent)
    # --> get_initialized_obj(self, input_dict, parent)
    # --> launch_u_or_c_for_relatedsets(self, input_dict_list, *args)
    #
    # The model of child class must implement:
    # 
    # --> match_obj_fields_to_dict(self, input_dict, parent)
    #
    matchattr = 'name'
    update_fields_to_exclude = ['id']
    is_bulk_create = False

    def update_or_create_parentrelateds(self, input_dict_list, parent,
                                        *args):
        # The init_objs is the (possibly empty) set of previously
        # existing objs for the focal parent (received as parameter)
        qs = self.get_parentqueryset(parent)
        init_objs = list(qs)
        curr_objs, new_objs = self.prep_parentrelateds(input_dict_list,
                                    init_objs, parent, *args)

        self.impl_obj_changes_to_db(curr_objs, new_objs, init_objs)

        self.launch_u_or_c_for_relatedsets(input_dict_list, *args)

        # The return value possibly used in other
        # 'launch_u_or_c_for_relatedsets'. The plus performs
        # concatenation of two lists.
        return curr_objs + new_objs

    def prep_parentrelateds(self, input_dict_list, init_objs, parent,
                            *args):
        # We obtain two sets of objects, based on the input_dict_list:
        # current ones are a subset of initial ones (init_objs), and new
        # ones that were not in init_objs.
        curr_objs = list()
        new_objs = list()
        for input_dict in input_dict_list:
            try:
                obj = next(o for o in init_objs if
                        getattr(o, self.matchattr) == \
                                input_dict[self.matchattr])
                curr_objs.append(obj)
            except StopIteration:
                # In order to initialize the object, all mandatory
                # fields need to be assigned a value. This is not the
                # final set of object field values.
                obj = self.get_initialized_obj(input_dict, parent)
                new_objs.append(obj)
            except Exception as e:
                print(e)
            finally:
                # We update all object fields based on the dict.
                # All object models need to have this method!
                obj.match_obj_fields_to_dict(input_dict, *args)
                # Store the object for the second looping of
                # input_dict_list in 'launch_u_or_c_for_each...'.
                input_dict['obj'] = obj
        return curr_objs, new_objs

    def impl_obj_changes_to_db(self, curr_objs, new_objs, init_objs):
        # Three steps to save the right results and just the right
        # results to the database: (1) update changes to the current ones,
        # (2) create the new ones and (3) delete the obsolete ones.
        # STEP 1
        if curr_objs:
            # We update all other fields except 'id' and 'course'
            fields_to_update = [f.name for f in self.model._meta.fields
                        if f.name not in self.update_fields_to_exclude]
            self.bulk_update(curr_objs, fields_to_update)
        # STEP 2
        if new_objs:
            if self.is_bulk_create:
                self.bulk_create(new_objs)
            else:
                for obj in new_objs:
                    obj.save()
        # STEP 3
        obsolete_id_set = {obj.id for obj in init_objs} \
                            - {obj.id for obj in curr_objs}
        if obsolete_id_set:
            self.filter(id__in=obsolete_id_set).delete()
